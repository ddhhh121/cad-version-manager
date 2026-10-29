import math
from pathlib import Path


def generate_preview(file_path: str) -> dict:
    """生成文件预览，返回 SVG 内容或提示信息"""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".dxf":
        return generate_dxf_preview(str(path))
    elif ext == ".dwg":
        return {"type": "unsupported", "message": "DWG 文件暂不支持在线预览，请下载后查看"}
    else:
        return {"type": "unsupported", "message": f"不支持 {ext} 格式的在线预览"}


def generate_dxf_preview(file_path: str) -> dict:
    """从 DXF 文件生成简化 SVG"""
    try:
        import ezdxf

        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        # 收集所有实体的坐标
        points = []
        lines = []
        circles = []
        arcs = []
        texts = []

        for entity in msp:
            dxftype = entity.dxftype()

            if dxftype == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                points.extend([(start.x, start.y), (end.x, end.y)])
                lines.append(((start.x, start.y), (end.x, end.y)))

            elif dxftype == "CIRCLE":
                center = entity.dxf.center
                radius = entity.dxf.radius
                points.extend([
                    (center.x - radius, center.y - radius),
                    (center.x + radius, center.y + radius),
                ])
                circles.append((center.x, center.y, radius))

            elif dxftype == "ARC":
                center = entity.dxf.center
                radius = entity.dxf.radius
                points.extend([
                    (center.x - radius, center.y - radius),
                    (center.x + radius, center.y + radius),
                ])
                arcs.append({
                    "cx": center.x,
                    "cy": center.y,
                    "r": radius,
                    "start": entity.dxf.start_angle,
                    "end": entity.dxf.end_angle,
                })

            elif dxftype in ("TEXT", "MTEXT"):
                if dxftype == "TEXT":
                    pos = entity.dxf.insert
                    text = entity.dxf.text
                else:
                    pos = entity.dxf.insert
                    text = entity.text if hasattr(entity, 'text') else ""
                if text:
                    points.append((pos.x, pos.y))
                    texts.append({"x": pos.x, "y": pos.y, "text": text[:50]})

            elif dxftype == "LWPOLYLINE":
                for point in entity.get_points():
                    points.append((point[0], point[1]))

            elif dxftype == "POLYLINE":
                for vertex in entity.vertices:
                    points.append((vertex.dxf.location.x, vertex.dxf.location.y))

        if not points:
            return {"type": "svg", "content": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="50" y="50" text-anchor="middle" fill="#999">空图纸</text></svg>'}

        # 计算边界
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # 添加边距
        margin = max((max_x - min_x), (max_y - min_y)) * 0.05
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin

        width = max_x - min_x
        height = max_y - min_y

        # 生成 SVG
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {width} {height}" ',
            f'width="800" height="600" style="background: #fff;">',
        ]

        # 绘制线段
        for (x1, y1), (x2, y2) in lines:
            svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="0.5"/>')

        # 绘制圆
        for cx, cy, r in circles:
            svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#333" stroke-width="0.5"/>')

        # 绘制弧
        for arc in arcs:
            cx, cy, r = arc["cx"], arc["cy"], arc["r"]
            start_angle = math.radians(arc["start"])
            end_angle = math.radians(arc["end"])

            x1 = cx + r * math.cos(start_angle)
            y1 = cy + r * math.sin(start_angle)
            x2 = cx + r * math.cos(end_angle)
            y2 = cy + r * math.sin(end_angle)

            large_arc = 1 if (end_angle - start_angle) > math.pi else 0
            svg_parts.append(f'<path d="M {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2}" fill="none" stroke="#333" stroke-width="0.5"/>')

        # 绘制文字
        font_size = max(width, height) * 0.02
        for t in texts:
            svg_parts.append(f'<text x="{t["x"]}" y="{t["y"]}" font-size="{font_size}" fill="#666">{escape_xml(t["text"])}</text>')

        svg_parts.append('</svg>')

        return {"type": "svg", "content": "".join(svg_parts)}

    except ImportError:
        return {"type": "unsupported", "message": "DXF 预览需要安装 ezdxf 库"}
    except Exception as e:
        return {"type": "error", "message": f"预览生成失败: {str(e)}"}


def escape_xml(text: str) -> str:
    """转义 XML 特殊字符"""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))
