#!/usr/bin/env python3
"""
CL17 Chlorine Analyzer Simulator
Generates realistic chlorine readings and writes to Modbus register 0
Pairs with hmi.py and hydrophobic.py
"""
import time
import math
import random
from pymodbus.client import ModbusTcpClient

MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020
REGISTER_ADDR = 0
UPDATE_INTERVAL = 2.0

# state variables - replacing self from the old class
start_time = time.time()
base_drift = 0.0
last_clean_time = time.time()
next_clean_interval = random.uniform(600, 1800)
warmup_seconds = 60.0



def compute_normal_value(now):
    global base_drift, last_clean_time, next_clean_interval
    elapsed = now - start_time

    diurnal = 4.0 + 2.5 * math.sin((elapsed / 3600.0) * (2 * math.pi / 12.0))

    if random.random() < 0.05:
        base_drift += random.uniform(-0.05, 0.05)
        base_drift = max(-1.5, min(1.5, base_drift))

    if elapsed < warmup_seconds:
        warmup_factor = elapsed / warmup_seconds
    else:
        warmup_factor = 1.0

    since_last_clean = now - last_clean_time
    cleaning = 0.0
    if since_last_clean > next_clean_interval:
        dip_depth = random.uniform(0.8, 2.0)
        dip_duration = random.uniform(30, 120)
        phase = min(1.0, (since_last_clean - next_clean_interval) / dip_duration)
        cleaning = -dip_depth * (1.0 - phase)
        if phase >= 1.0:
            last_clean_time = now
            next_clean_interval = random.uniform(600, 1800)
            cleaning = 0.0

    noise = random.uniform(-0.25, 0.25)
    mg = (diurnal + base_drift + cleaning) * warmup_factor + noise
    mg = max(0.0, min(12.0, mg))
    return mg

if __name__ == "__main__":
    print("[*] CL17 Simulator starting...")
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    client.connect()
    
    while True:
        now = time.time()
        mg = compute_normal_value(now)
        register_value = int(round(mg * 10))
        client.write_register(REGISTER_ADDR, register_value)
        print(f"[+] CL17: {mg:.2f} mg/L → register value {register_value}")
        time.sleep(UPDATE_INTERVAL)