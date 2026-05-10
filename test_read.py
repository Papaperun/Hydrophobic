from pymodbus.client import ModbusTcpClient

c = ModbusTcpClient("127.0.0.1", port=5020)
c.connect()
result = c.read_holding_registers(address=0, count=1)
print(f"[*] Register 0 (Chlorine): {result.registers[0]} = {result.registers[0] / 10:.2f} mg/L")
c.close()