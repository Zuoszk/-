#!/usr/bin/env python3
import asyncio
import random
import uuid
import json
from datetime import datetime
from dataclasses import dataclass, asdict
import aiohttp

# -------------------------------------------------------------------
# 1. 定義切削資料結構
# -------------------------------------------------------------------
@dataclass
class CuttingData:
    timestamp: str
    tool_id: str
    spindle_speed: float
    feed_rate: float
    cutting_force: float
    temperature: float
    vibration: float
    wear_level: float

# -------------------------------------------------------------------
# 2. MCP 封包打包函式
# -------------------------------------------------------------------
def pack_mcp_message(data: CuttingData) -> dict:
    return {
        "header": {
            "protocol_version": "1.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": data.timestamp
        },
        "context": asdict(data),
        "payload": {
            "request": "模擬切削資料匯報"
        }
    }

# -------------------------------------------------------------------
# 3. DataCollector：只用模擬資料
# -------------------------------------------------------------------
class DataCollector:
    def __init__(self, tool_id: str, freq_hz: float = 10.0):
        self.tool_id = tool_id
        self.interval = 1.0 / freq_hz

    async def start(self, callback):
        while True:
            # 產生一筆 CuttingData
            now = datetime.now().isoformat()
            cd = CuttingData(
                timestamp     = now,
                tool_id       = self.tool_id,
                spindle_speed = random.uniform(800, 2000),
                feed_rate     = random.uniform(0.05, 0.3),
                cutting_force = random.uniform(100, 500),
                temperature   = random.uniform(30, 70),
                vibration     = random.uniform(0, 0.05),
                wear_level    = random.uniform(0, 0.1)
            )
            await callback(cd)
            await asyncio.sleep(self.interval)

# -------------------------------------------------------------------
# 4. 傳送到 MCP Server 的實作（HTTP POST 範例）
# -------------------------------------------------------------------
async def send_to_mcp_server(data: CuttingData):
    mcp_msg = pack_mcp_message(data)
    # ← 加上 /mcp/data 路徑
    url = "http://192.168.0.106:8000/mcp/data"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=mcp_msg) as resp:
            if resp.status != 200:
                body = await resp.text()
                print(f"[Error] HTTP {resp.status}: {body}")
            else:
                print(f"[OK] Sent {mcp_msg['header']['message_id']}")

# -------------------------------------------------------------------
# 5. 啟動
# -------------------------------------------------------------------
async def main():
    collector = DataCollector(tool_id="T01", freq_hz=10.0)
    await collector.start(send_to_mcp_server)

if __name__ == "__main__":
    asyncio.run(main())
