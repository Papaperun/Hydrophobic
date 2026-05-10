from pymodbus.simulator import SimData, SimDevice, DataType
from pymodbus.server import StartAsyncTcpServer
import asyncio

devices = [
    SimDevice(1, simdata=(
        [SimData(0, values=[0] * 100, datatype=DataType.BITS)],       # coils
        [SimData(0, values=[0] * 100, datatype=DataType.BITS)],       # discrete inputs
        [SimData(0, values=[0] * 100, datatype=DataType.REGISTERS)],  # holding registers
        [SimData(0, values=[0] * 100, datatype=DataType.REGISTERS)],  # input registers
    ))
]

async def run_server():
    print("[+] Modbus TCP server starting on 0.0.0.0:5020")
    print("[*] Waiting for connections...")
    await StartAsyncTcpServer(context=devices, address=("0.0.0.0", 5020))

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n Server stopped.")