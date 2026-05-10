#!/usr/bin/env python3
"""
CL17 HMI - Chlorine Analyzer Display
Reads from Modbus register 0, displays real time color and sparkline
Lab use only - pairs with cl17.py, mbsever2.py, and hydrophobic.py
"""
import tkinter as tk
from tkinter import messagebox
import math
import time
import collections
from pymodbus.client import ModbusTcpClient

# -------------- Configuration --------------
MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020
REGISTER_ADDR = 0
UPDATE_INTERVAL_MS = 2000
HISTORY_LEN = 60

# -------------- History buffer --------------
history = collections.deque(maxlen=HISTORY_LEN)

# -------------- Utility functions --------------
def mg_to_rgb_hex(mg):
    """Convert mg/L to color (pink/magenta scale)"""
    mg = max(0.0, min(10.0, mg))
    if mg <= 0.05: return "#ffffff"      # clear
    elif mg <= 0.5: return "#fff0f8"     # very faint pink
    elif mg <= 1.0: return "#ffe0f0"     # light pink
    elif mg <= 2.0: return "#ffc0e8"     # rose
    elif mg <= 4.0: return "#ff90d8"     # medium magenta
    elif mg <= 6.0: return "#ff60c8"     # strong magenta
    elif mg <= 8.0: return "#e040b0"     # deep purple-pink
    else:           return "#c000a0"     # dark purple (off-scale high)

def read_chlorine():
    """Read register 0 from Modbus server, return mg/L value"""
    try:
        c = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
        c.connect()
        result = c.read_holding_registers(address=REGISTER_ADDR, count=1)
        c.close()
        if result.isError():
            return None
        return result.registers[0] / 10.0
    except:
        return None

# -------------- App --------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CL17 Chlorine Analyzer HMI")
        self.root.configure(bg="black")
        self.running = True

        # Color canvas
        self.canvas = tk.Canvas(root, width=400, height=200, bg="#ffffff", highlightthickness=2)
        self.canvas.pack(padx=12, pady=(12, 4))

        # Value display
        self.value_label = tk.Label(root, text="0.00 mg/L", font=("Arial", 24, "bold"), fg="white", bg="black")
        self.value_label.pack(pady=(4, 2))

        # Status label
        self.status_label = tk.Label(root, text="Status: Connecting...", font=("Arial", 10), fg="yellow", bg="black")
        self.status_label.pack()

        # Recent readings list
        bottom_frame = tk.Frame(root, bg="black")
        bottom_frame.pack(fill=tk.BOTH, expand=False, padx=8, pady=(6, 12))

        left = tk.Frame(bottom_frame, bg="black")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        tk.Label(left, text="Recent readings (most recent on top):", fg="white", bg="black").pack(anchor="w")
        self.lst = tk.Listbox(left, height=6, width=28)
        self.lst.pack()

        # Sparkline
        right = tk.Frame(bottom_frame, bg="black")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Sparkline:", fg="white", bg="black").pack(anchor="w")
        self.spark = tk.Canvas(right, width=300, height=60, bg="#222222", highlightthickness=0)
        self.spark.pack()

        # Start update loop
        self._update_ui()

        # Graceful close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _update_ui(self):
        if not self.running:
            return

        mg = read_chlorine()

        if mg is None:
            self.status_label.config(text="Status: No Modbus connection", fg="red")
            self.root.after(UPDATE_INTERVAL_MS, self._update_ui)
            return

        # Append to history
        history.append((time.time(), mg))

        # Update color canvas
        color = mg_to_rgb_hex(mg)
        self.canvas.configure(bg=color)

        # Update value label
        self.value_label.config(text=f"{mg:.2f} mg/L")

        # Update status
        self.status_label.config(text="Status: Live | Modbus OK", fg="green")

        # Update recent readings list
        self.lst.delete(0, tk.END)
        for ts, val in list(history)[-10:][::-1]:
            tstr = time.strftime("%H:%M:%S", time.localtime(ts))
            self.lst.insert(tk.END, f"{tstr}  {val:5.2f} mg/L")

        # Update sparkline
        self._draw_sparkline()

        # Schedule next update
        self.root.after(UPDATE_INTERVAL_MS, self._update_ui)

    def _draw_sparkline(self):
        data = [v for (_, v) in history]
        if not data:
            self.spark.delete("all")
            return
        w = int(self.spark["width"])
        h = int(self.spark["height"])
        margin = 4
        plot_w = w - 2 * margin
        plot_h = h - 2 * margin
        n = len(data)
        maxv = max(max(data), 12.0)
        minv = min(min(data), 0.0)
        span = maxv - minv if maxv > minv else 1.0

        self.spark.delete("all")

        for y_frac in (0.0, 0.5, 1.0):
            y = margin + y_frac * plot_h
            self.spark.create_line(margin, y, margin + plot_w, y, fill="#444444")

        if n == 1:
            x = margin + plot_w / 2
            y = margin + (1 - (data[0] - minv) / span) * plot_h
            self.spark.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#00ff00")
        else:
            points = []
            for i, v in enumerate(data):
                x = margin + (i / (n - 1)) * plot_w
                y = margin + (1 - (v - minv) / span) * plot_h
                points.append((x, y))

            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                self.spark.create_line(x1, y1, x2, y2, width=2, smooth=True, fill="#00ff88")

            lx, ly = points[-1]
            self.spark.create_oval(lx - 3, ly - 3, lx + 3, ly + 3, fill="#00ff88", outline="")

    def _on_close(self):
        if messagebox.askokcancel("Quit", "Close HMI?"):
            self.running = False
            self.root.destroy()

# -------------- Main --------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()