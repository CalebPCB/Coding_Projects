import tkinter as tk
import platform
import socket
import psutil
import requests
import threading

API_URL = "http://your-api-server/api/report"  # Change this to your API endpoint

class RMMAgent:
    def __init__(self, root):
        self.root = root
        root.title("NerdAgent")
        root.geometry("300x300")
        root.resizable(False, False)

        self.label = tk.Label(root, text="Collecting system info...", justify="left", anchor="w")
        self.label.pack(fill="both", padx=10, pady=10)

        self.update_and_send()
        self.schedule_refresh()

    def collect_data(self):
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "N/A"
        data = {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_version": platform.version(),
            "cpu": platform.processor(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ip": ip,
        }
        return data

    def update_gui(self):
        data = self.collect_data()
        display = (
            f"Hostname: {data['hostname']}\n"
            f"OS: {data['os']} {data['os_version'][:15]}\n"
            f"CPU: {data['cpu'][:20]}\n"
            f"Memory: {data['memory_gb']} GB\n"
            f"IP: {data['ip']}"
        )
        self.label.config(text=display)

    def send_data(self):
        def _send():
            data = self.collect_data()
            try:
                response = requests.post(API_URL, json=data, timeout=5)
                print(f"Sent data, status code: {response.status_code}")
            except Exception as e:
                print(f"Failed to send data: {e}")

        threading.Thread(target=_send, daemon=True).start()

    def update_and_send(self):
        self.update_gui()
        self.send_data()

    def schedule_refresh(self):
        self.update_and_send()
        self.root.after(60000, self.schedule_refresh)  # 60 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = RMMAgent(root)
    root.mainloop()
