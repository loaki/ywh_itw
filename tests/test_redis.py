import os
import sys
import time
import inspect
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from tools.redis_queue import RedisQueue


G_ITEM = None
G_COUNT = 0
G_CLASSES = set()
mutex = threading.Lock()


def print_lock(class_call, item):
    mutex.acquire()
    print(class_call, item)
    mutex.release()


def set_global_item(item):
    global G_ITEM
    global G_COUNT
    G_ITEM = item
    G_COUNT += 1
    stack = inspect.stack()
    class_call = stack[1][0].f_locals["self"]
    G_CLASSES.add(hex(id(class_call)))
    print_lock(class_call, item)


def test_push():
    time.sleep(1)
    global G_ITEM
    global G_COUNT
    G_ITEM = None
    G_COUNT = 0
    rq = RedisQueue("key_test", "chan_test", set_global_item)
    rq.queue_push("test1_1")
    rq.queue_push("test1_2")
    rq.process_queue()
    assert G_ITEM == "test1_2"
    assert G_COUNT == 2


def test_listen():
    global G_ITEM
    global G_COUNT
    G_ITEM = None
    G_COUNT = 0
    rq = RedisQueue("key_test", "chan_test", set_global_item)
    rq.thread_listen()
    time.sleep(2)
    rq.queue_push("test2_1")
    rq.queue_push("test2_2")
    time.sleep(2)
    assert G_ITEM == "test2_2"
    assert G_COUNT == 2
    rq.stop_threads()


def test_multithreads():
    global G_ITEM
    global G_COUNT
    global G_CLASSES
    G_ITEM = None
    G_COUNT = 0
    G_CLASSES = set()
    rq = RedisQueue("key_test", "chan_test", None)
    rq_first = RedisQueue("key_test", "chan_test", set_global_item)
    rq_sec = RedisQueue("key_test", "chan_test", set_global_item)
    rq_first.thread_listen()
    rq_sec.thread_listen()
    time.sleep(5)
    for i in range(10):
        rq.queue_push(f"test3_{i}")
    time.sleep(2)
    assert G_COUNT == 10
    assert len(G_CLASSES) == 2
    rq_first.stop_threads()
    rq_sec.stop_threads()


if __name__ == "__main__":
    test_push()
    test_listen()
    test_multithreads()
