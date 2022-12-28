import multiprocessing


class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    def reset(self):
        self.val = multiprocessing.Value('i', 0)

    @property
    def value(self):
        return self.val.value
