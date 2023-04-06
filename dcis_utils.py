from termcolor import cprint, colored
import functools
import traceback
import time
from datetime import datetime

def print_function_dec(func):
    """This function is written to help write out time of functions and get exceptions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(colored("Going into ", 'magenta') + colored(func.__name__, 'green') + colored(f" at time {datetime.utcnow()}", "magenta"))
        try:
            result = func(*args, **kwargs)
            print(colored("Done with ", 'magenta') + colored(func.__name__, 'green') + colored(f" in {time.time() - start_time} sec", "magenta"))
            return result
        except Exception as e:
            cprint(f"Caught an exception at {func.__name__}: '{str(e)}'", "red")
            traceback.print_exc()
    return wrapper