import tkinter as tk
import platform
import socket
import psutil
import requests
import threading

API_URL_REPORT = "http://100.24.4.189:8000/api/report"  # Your API endpoint

class RMMAgent:
    def __init__(self, root):
        self.root = root
        root.title("NerdAgent")
        root.geometry("350x300")
        root.resizable(False, False)

        self.user_id = None

        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_user_input()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_user_input(self):
        self.clear_frame()
        tk.Label(self.frame, text="Enter your User Name:", anchor="w").pack(fill="x", pady=(0,5))
        self.user_entry = tk.Entry(self.frame)
        self.user_entry.pack(fill="x", pady=(0,10))

        tk.Button(self.frame, text="Submit", command=self.submit_user_id).pack()

        self.status_label = tk.Label(self.frame, text="", fg="red")
        self.status_label.pack(pady=(10,0))

    def submit_user_id(self):
        uid = self.user_entry.get().strip()
        if not uid:
            self.status_label.config(text="User Name cannot be empty.")
            return
        # Optional: add more validation here (e.g., no spaces or special chars)
        self.user_id = uid
        self.start_reporting()

    def collect_data(self):
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "N/A"
        data = {
            "user_id": self.user_id,
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
            f"User Name: {self.user_id}\n\n"
            f"Hostname: {data['hostname']}\n"
            f"OS: {data['os']} {data['os_version'][:15]}\n"
            f"CPU: {data['cpu'][:20]}\n"
            f"Memory: {data['memory_gb']} GB\n"
            f"IP: {data['ip']}"
        )
        self.info_label.config(text=display)

    def send_data(self):
        def _send():
            data = self.collect_data()
            try:
                response = requests.post(API_URL_REPORT, json=data, timeout=5)
                print(f"Sent data, status code: {response.status_code}")
            except Exception as e:
                print(f"Failed to send data: {e}")

        threading.Thread(target=_send, daemon=True).start()

    def update_and_send(self):
        self.update_gui()
        self.send_data()

    def schedule_refresh(self):
        self.update_and_send()
        self.root.after(60000, self.schedule_refresh)  # every 60 seconds

    def start_reporting(self):
        self.clear_frame()
        self.info_label = tk.Label(self.frame, text="", justify="left", anchor="w", font=("Courier", 10))
        self.info_label.pack(fill="both", expand=True)

        tk.Button(self.frame, text="Change User Name", command=self.show_user_input).pack(pady=10)

        self.schedule_refresh()

if __name__ == "__main__":
    root = tk.Tk()
    app = RMMAgent(root)
    root.mainloop()
