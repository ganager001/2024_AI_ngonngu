import psutil
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio


class SystemStatsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.keep_running = True
        asyncio.create_task(self.send_stats())

    async def disconnect(self, close_code):
        self.keep_running = False

    async def send_stats(self):
        while self.keep_running:
            cpu = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            stats = {
                'cpu': cpu,
                'memory': memory,
                'disk': disk
            }
            await self.send(text_data=json.dumps(stats))
            await asyncio.sleep(1)  # Update mỗi giây
