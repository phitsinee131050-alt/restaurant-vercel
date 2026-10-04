import io
def qr_png(url):
    import qrcode
    buf = io.BytesIO(); qrcode.make(url).save(buf, "PNG"); return buf.getvalue()

def lan_ip():  # IP ของเครื่องนี้ในวง Wi-Fi (มือถือต้องใช้ IP นี้ ใช้ 127.0.0.1 ไม่ได้)
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
    except OSError: return "127.0.0.1"
    finally: s.close()
