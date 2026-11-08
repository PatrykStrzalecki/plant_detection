import os
import random
import time
import aiohttp
import redis.asyncio as aioredis
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class PerformanceTesterClient:
    def __init__(self, base_url: str = BACKEND_URL, redis_url: str = REDIS_URL):
        self.base_url = base_url
        self.redis_client = aioredis.from_url(redis_url, decode_responses=True)
        self.running = False
        
        self.tracking_data = {}
        self.early_results = {}
        
        self.http_session: Optional[aiohttp.ClientSession] = None

    async def start_listener(self):
        self.running = True
        pubsub = self.redis_client.pubsub()
        await pubsub.psubscribe("task_status_*")
        
        try:
            async for message in pubsub.listen():
                if not self.running:
                    break
                if message["type"] == "pmessage":
                    channel: str = message["channel"]
                    if channel.startswith("task_status_"):
                        status = message["data"]
                        if status == "SUCCESS":
                            receive_time = time.time()
                            task_id = int(channel.split("_")[-1])

                            if task_id in self.tracking_data and self.tracking_data[task_id]["received_at"] is None:
                                self.tracking_data[task_id]["received_at"] = receive_time
                            else:
                                self.early_results[task_id] = receive_time
                                
        except Exception as e:
            print(f"Error in testing redis listener: {e}")
        finally:
            await pubsub.close()

    async def _get_task_result(self, task_id: int) -> Optional[dict]:
        if self.http_session is None or self.http_session.closed:
            self.http_session = aiohttp.ClientSession()

        url = f"{self.base_url}/task-status/{task_id}"
        try:
            async with self.http_session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Error fetching task result for perf test: {e}")
        return None
        
    async def upload_image(self, images_folder: Path):
        if self.http_session is None or self.http_session.closed:
            self.http_session = aiohttp.ClientSession()

        try:
            image_files = [f for f in images_folder.iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png"}]
            if not image_files:
                print("No image files found.")
                return
            
            image_path = random.choice(image_files)
            
            with open(image_path, "rb") as img_file:
                data = aiohttp.FormData()
                data.add_field('file', img_file, filename=image_path.name, content_type='image')
                
                send_time = time.time()
                async with self.http_session.post(f"{self.base_url}/upload-image", data=data) as response:
                    if response.status == 202:
                        result = await response.json()
                        task_id = int(result.get("id"))

                        early_receive_time = self.early_results.pop(task_id, None)

                        self.tracking_data[task_id] = {
                            "sent_at": send_time,
                            "received_at": early_receive_time,
                            "category": None
                        }
                    else:
                        print(f"Upload failed. Status: {response.status}")

        except Exception as e:
            print(f"Upload error: {e}")

    def clear_tracker(self):
        self.tracking_data.clear()
        self.early_results.clear()

    async def close_connections(self):
        self.running = False
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()

    def stop(self):
        self.running = False