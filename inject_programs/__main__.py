from tools.redis_queue import RedisQueue
from .mdb_programs import MdbPrograms


mdb_prog = MdbPrograms()
rq = RedisQueue(
    queue_key="ywh_programs", channel="ywh_channel", process_func=mdb_prog.create_or_update_program
)
rq.thread_listen()
