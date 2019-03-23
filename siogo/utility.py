import time

from . import exceptions

def with_retries(func, handled, retries, *, delay=0):
    for i in range(retries):
        print("Retry {} executing {}".format(i, func))
        time.sleep(delay)
        try:
            return func()
        except handled:
            if i+1 == retries:
                raise exceptions.TooManyRetries("Caught exception after {} retries.".format(retries))
