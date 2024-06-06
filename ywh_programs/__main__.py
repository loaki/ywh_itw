import schedule

from .ywh_api import YwhAPI
from tools.redis_queue import RedisQueue


rq = RedisQueue(queue_key="ywh_programs", channel="ywh_channel")
ywh_api = YwhAPI(rq=rq)

schedule.every(10).minutes.do(ywh_api.fetch_programs)

while True:
    schedule.run_pending()
