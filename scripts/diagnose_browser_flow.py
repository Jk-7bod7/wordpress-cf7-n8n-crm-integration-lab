import urllib.request
import socket
import json

print("=== 1. Inspecting http://127.0.0.1:8080 ===")
try:
    req = urllib.request.Request("http://127.0.0.1:8080")
    with urllib.request.urlopen(req, timeout=3) as r:
        html = r.read().decode("utf-8", errors="replace")
        print("HTTP Status:", r.status)
        print("Server Header:", r.headers.get("Server", "None"))
        print("Content-Type:", r.headers.get("Content-Type", "None"))
        has_wp = "wp-" in html or "wordpress" in html.lower()
        has_cf7 = "wpcf7" in html or "contact-form-7" in html.lower()
        print("WordPress Detected:", has_wp)
        print("Contact Form 7 Detected:", has_cf7)
        if "<title>" in html:
            title = html.split("<title>")[1].split("</title>")[0]
            print("Document Title:", title)
except Exception as e:
    print("Failed to query 8080:", e)

print("\n=== 2. Probing /json/list (CEF remote debugging endpoint) ===")
try:
    req = urllib.request.Request("http://127.0.0.1:8080/json/list")
    with urllib.request.urlopen(req, timeout=3) as r:
        data = json.loads(r.read().decode("utf-8"))
        print(f"Active CEF tabs ({len(data)}):")
        for item in data[:5]:
            print(" - Title:", item.get("title"), "| URL:", item.get("url"))
except Exception as e:
    print("Failed to query /json/list:", e)

print("\n=== 3. Probing Stack Service Ports ===")
services = [
    ("WordPress (Docker target)", 8080),
    ("n8n Webhook Engine", 5678),
    ("Mock CRM (FastAPI)", 8000),
    ("Mailpit Web UI", 8025),
    ("Mailpit SMTP", 1025)
]

for name, port in services:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    res = s.connect_ex(("127.0.0.1", port))
    s.close()
    status_str = "OPEN / LISTENING" if res == 0 else "OFFLINE (Connection Refused)"
    print(f"{name:<28} [Port {port:<4}]: {status_str}")
