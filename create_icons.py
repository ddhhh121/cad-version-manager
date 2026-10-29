"""生成 PWA 图标"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """创建简单的 CAD 图标"""
    img = Image.new('RGBA', (size, size), (26, 26, 46, 255))
    draw = ImageDraw.Draw(img)

    # 绘制一个简单的 CAD 图标（齿轮 + 文件）
    margin = size // 6

    # 绘制文件形状
    file_color = (46, 90, 136, 255)
    draw.rectangle(
        [margin, margin, size - margin, size - margin],
        fill=file_color
    )

    # 绘制折角
    fold_size = size // 5
    draw.polygon([
        (size - margin - fold_size, margin),
        (size - margin, margin + fold_size),
        (size - margin - fold_size, margin + fold_size),
    ], fill=(35, 75, 115, 255))

    # 绘制线条（代表 CAD）
    line_color = (255, 255, 255, 200)
    line_width = max(2, size // 40)
    center_x = size // 2
    center_y = size // 2 + margin // 4

    # 水平线
    draw.line(
        [margin * 2, center_y, size - margin * 2, center_y],
        fill=line_color, width=line_width
    )

    # 垂直线
    draw.line(
        [center_x, margin * 2, center_x, size - margin * 2],
        fill=line_color, width=line_width
    )

    # 对角线
    draw.line(
        [margin * 2, margin * 2, size - margin * 2, size - margin * 2],
        fill=line_color, width=line_width
    )

    img.save(output_path)
    print(f"Created icon: {output_path}")

if __name__ == "__main__":
    public_dir = os.path.join(os.path.dirname(__file__), "frontend", "public")
    create_icon(192, os.path.join(public_dir, "icon-192.png"))
    create_icon(512, os.path.join(public_dir, "icon-512.png"))
    print("Icons created successfully!")
