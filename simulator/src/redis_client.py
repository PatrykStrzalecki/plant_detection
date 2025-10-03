import os
import random
import aiohttp
import redis.asyncio as aioredis

from pathlib import Path
from typing import Callable, Optional

from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
BACKEND_URL = os.getenv("BACKEND_URL")

class SimulatorRedisClient:
    def __init__(self, base_url: str = BACKEND_URL, redis_url: str = REDIS_URL):
        self.base_url = base_url
        self.redis_client = aioredis.from_url(redis_url, decode_responses=True)
        self.running = False
        self.category_callbacks = {}
        self.plants = {}

    async def start_listener(self):
        self.running = True
        pubsub = self.redis_client.pubsub()
        await pubsub.psubscribe("task_status_*")
        try:
            async for message in pubsub.listen():
                if not self.running:
                    break
                print(f"Received message: {message}")
                if message["type"] == "pmessage":
                    channel : str = message["channel"]
                    if channel.startswith("task_status_"):
                        status = message["data"]
                        if status == "SUCCESS":
                            task_id = int(channel.split("_")[-1])
                            if task_id in self.category_callbacks and task_id in self.plants:
                                result = await self._get_task_result(task_id)
                                if result:
                                    category = result.get("category")
                                    if category:
                                        print(f"Task {task_id} completed with category {category}.\n")
                                        callback = self.category_callbacks.get(task_id)
                                        plant_id = self.plants.get(task_id)
                                        callback(int(category), plant_id)
                                        del self.category_callbacks[task_id]
                                        del self.plants[task_id]

        except Exception as e:
            print(f"Error in redis listener: {e}")
        finally:
            await pubsub.close()

    async def _get_task_result(self, task_id: int) -> Optional[dict]:
        url = f"{self.base_url}/task-status/{task_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Failed to get task result for task {task_id}, status code: {response.status}")
                        return None
        except Exception as e:
            print(f"Error fetching task result: {e}")
            return None
        
    async def upload_image(self, images_folder: Path, plant_id : int, callback: Callable):
        try:
            image_files = [f for f in images_folder.iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png"}]
            if not image_files:
                print("No image files found in the specified folder.")
                return
            
            image_path = random.choice(image_files)
            async with aiohttp.ClientSession() as session:
                with open(image_path, "rb") as img_file:
                    data = aiohttp.FormData()
                    data.add_field('file', img_file, filename = image_path.name, content_type = 'image')
                    async with session.post(f"{self.base_url}/upload-image", data = data) as response:
                        if response.status == 202:
                            result : dict = await response.json()
                            task_id = int(result.get("id"))
                            self.category_callbacks[task_id] = callback
                            self.plants[task_id] = plant_id
                            print(f"Image {image_path.name} uploaded successfully with task ID {task_id}. Waiting for result...")
                        else:
                            error_text = await response.text()
                            print(f"Failed to upload image, status code: {response.status}, error: {error_text}")

        except Exception as e:
            print(f"Error uploading image: {e}")

    def stop(self):
        self.running = False