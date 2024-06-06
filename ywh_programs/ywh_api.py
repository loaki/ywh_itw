import os
import dotenv
import logging
import requests

from tools.redis_queue import RedisQueue


class YwhAPI:
    def __init__(self, rq: RedisQueue) -> None:
        # Load environment variables
        dotenv.load_dotenv()

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

        self.session = requests.Session()
        self.login()
        self.rq = rq
        self.max_login = 2

    def login(self) -> None:
        """
        Log in to the YesWeHack API
        """
        payload = {"email": os.getenv("YWH_EMAIL"), "password": os.getenv("YWH_PASSWORD")}
        response = requests.post("https://api.yeswehack.com/login", json=payload)
        if response.status_code == requests.codes.ok and response.json().get("token"):
            self.session.headers.update({"Authorization": f"Bearer {response.json().get('token')}"})
            self.logger.debug("Logged in successfully")
        else:
            self.logger.error(f"Failed to login: {response.text}")

    def fetch_programs(self, page: int = 1) -> None:
        """
        Fetch public programs from the YesWeHack API and push them to the Redis queue
        """
        nb_pages = 1
        while page <= nb_pages:
            params = {"filter[disabled]": 0, "filter[visibility]": "public", "page": page}
            response = self.session.get("https://api.yeswehack.com/programs", params=params)
            if response.status_code == requests.codes.ok:
                self.max_login = 2
                nb_pages = response.json().get("pagination", {}).get("nb_pages", 1)
                page += 1
                self.logger.debug(f"Fetched page {page - 1}/{nb_pages} programs")
                for program in response.json().get("items", []):
                    if program.get("title"):
                        self.rq.queue_push(
                            {
                                "title": program.get("title"),
                                "reports_count": program.get("reports_count"),
                            }
                        )
            elif response.status_code == 401 and self.max_login > 0:
                self.login()
                self.max_login -= 1
            else:
                self.logger.error(f"{response.status_code}")
                self.logger.error(f"Failed to fetch programs: {response.text}")
                break
