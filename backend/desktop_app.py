"""
CAD 版本管理器 - 桌面应用入口
使用 pywebview 创建原生桌面窗口
"""
import sys
import threading
import time
import webview
import uvicorn
import httpx
from pathlib import Path


def get_local_ip():
    """获取本机局域网 IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def start_server(host="0.0.0.0"):
    """在后台线程启动 FastAPI 服务器"""
    from app.main import app
    uvicorn.run(
        app,
        host=host,
        port=8000,
        log_level="warning",
        access_log=False,
    )


def wait_for_server(timeout=10):
    """等待服务器就绪"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get("http://127.0.0.1:8000/api/health", timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def main():
    """主函数 - 启动桌面应用"""
    # 获取本机 IP
    local_ip = get_local_ip()

    # 在后台线程启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 等待服务器就绪
    wait_for_server()

    # 创建原生窗口
    window = webview.create_window(
        title="CAD 图纸版本管理器",
        url="http://127.0.0.1:8000",
        width=1280,
        height=800,
        min_size=(800, 600),
        resizable=True,
        confirm_close=True,
        text_select=True,
    )

    # 启动窗口
    webview.start(debug=False)


if __name__ == "__main__":
    main()
