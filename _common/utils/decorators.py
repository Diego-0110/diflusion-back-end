import threading
def th_sf_singleton(cls):
    instances = {}
    lock = threading.Lock()
    def get_instance(*args, **kwargs):
        lock.acquire()
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        lock.release()
        return instances[cls]
    
    return get_instance