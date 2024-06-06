import os
import json
import redis
import dotenv
import threading
from typing import Callable


class RedisQueue:
    def __init__(self, queue_key: str, channel: str, process_func: Callable | None = None) -> None:
        dotenv.load_dotenv()
        self.client = redis.StrictRedis(
            host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0
        )
        self.running = True
        self.queue_key = queue_key
        self.channel = channel
        self.process_func = process_func

    def queue_push(self, item: dict) -> None:
        """
        Push an item to the Redis queue and publish a message to the channel
        """
        self.client.rpush(self.queue_key, json.dumps(item))
        self.client.publish(self.channel, "Item added to queue")

    def process_queue(self) -> None:
        """
        Process the queue by popping items and calling the process_func
        """
        while self.client.llen(self.queue_key) > 0:
            item = self.client.lpop(self.queue_key)
            if item:
                item = json.loads(item.decode("utf-8"))
                if self.process_func:
                    self.process_func(item)

    def listen_pubsub(self) -> None:
        """
        Listen to the Redis channel and process the queue when a message is received
        """
        pubsub = self.client.pubsub()
        pubsub.subscribe(self.channel)

        for message in pubsub.listen():
            if message["type"] == "message":
                self.process_queue()

    def thread_listen(self) -> None:
        """
        Start a thread to listen to the Redis channel
        """
        thread = threading.Thread(target=self.listen_pubsub)
        thread.daemon = True
        thread.start()

        while self.running:
            pass

    def stop_threads(self) -> None:
        """
        Stop the listening thread
        """
        self.running = False
