import os
import logging
from pymongo import MongoClient
import dotenv


class MdbPrograms:
    def __init__(self) -> None:
        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        myFormatter = logging.Formatter(
            "%(asctime)s - %(levelname)s : "
            + self.__class__.__name__
            + " - {%(filename)s:%(lineno)d} : %(message)s"
        )
        handler.setFormatter(myFormatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False

        dotenv.load_dotenv()
        self.client = MongoClient(
            f'mongodb://{os.getenv("MONGO_USERNAME")}:{os.getenv("MONGO_PASSWORD")}@{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}/'
        )
        self.logger.debug(self.client)
        self.db = self.client[os.getenv("MONGO_DB")]
        self.collection = self.db["programs"]

    def create_or_update_program(self, program: dict) -> None:
        """
        Create or update a program in the MongoDB collection
        """
        self.collection.update_one({"title": program["title"]}, {"$set": program}, upsert=True)
