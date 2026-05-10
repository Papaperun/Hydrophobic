# Hydrophobic — OT False Data Injection Lab

A Modbus TCP lab environment demonstrating false data injection 
against a simulated CL17 chlorine analyzer in a municipal water system.

Inspired by Mike Holcomb's Snowcrash tool.
Built by a Class A Licensed Water Treatment Operator with 22 years 
of municipal infrastructure experience.
python 3.11 
⚠️ Lab use only. Never use against systems you do not own.

---

## What This Demonstrates

Unauthenticated Modbus TCP register writes — one of the most common 
attack vectors in municipal OT environments. No credentials required. 
No physical access required. One command changes what the operator sees.

---

## Pipeline

cl17.py → MBhydrophobic.py → hmi.py
                ↑
          hydrophobic.py

---

## Files

| File | Purpose |
|------|---------|
| MBhydrophobic.py | Modbus TCP server — holds the register map |
| cl17.py | CL17 chlorine analyzer simulator — writes realistic values |
| hmi.py | Real time HMI display — color canvas and sparkline |
| hydrophobic.py | False data injection tool — attack tool |
| test_read.py | Diagnostic utility — manual register check |

---

## Requirements

pip install pymodbus

---

## Usage

Start the pipeline in this order — each component needs the previous one running:

1. Start the Modbus server
2. Start the CL17 simulator  
3. Start the HMI
4. Run hydrophobic.py separately to inject values

Windows users: a start_lab.bat file is included for convenience.
Linux/Mac users: open three terminals and run each file manually.

---

## The Attack

With the pipeline running, hydrophobic.py prompts for:
- Target IP (127.0.0.1 for local lab)
- Register address (0 for chlorine reading)
- Value to inject (0 = no chlorine, 120 = 12.0 mg/L off scale high)

The HMI canvas and sparkline show the injection in real time.
Every run is logged to hydrophobic_log.json for forensic review.

---

## Why This Matters

Modbus TCP has no built-in authentication. Any device on the network 
can read or write registers without credentials. In a real municipal 
water system this register might represent chlorine residual — 
the primary barrier between the distribution system and public health.

A false low reading causes an operator to increase chlorine feed 
unnecessarily. A false high reading causes them to shut it down.
Neither requires touching the hardware.

In a real chlorine-ammonia system a false low reading triggers 
an operator response — increasing ammonia feed to boost chlorine 
formation. Excess ammonia reacts with residual chlorine producing 
chloramines, driving residual further down, causing the operator 
to dose again. A single falsified register value can initiate a 
dosing cascade that degrades water quality across the entire 
distribution system — no physical access required.

---

## Credit

Inspired by Mike Holcomb's Snowcrash — go check out his work.