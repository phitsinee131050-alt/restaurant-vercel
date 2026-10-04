import os
from app import create_app
app = create_app()
if __name__ == "__main__":
    from app.services.qr_service import lan_ip
    print(f"\n  >>> เปิดจากมือถือ/แท็บเล็ต (ต้องอยู่ Wi-Fi เดียวกับคอม): http://{lan_ip()}:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG") == "1")
