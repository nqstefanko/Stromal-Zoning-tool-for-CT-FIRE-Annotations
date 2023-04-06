from termcolor import cprint, colored
import functools
import traceback
import time
from datetime import datetime
import numpy as np

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

def generate_fiber(start=0, end=513, min_len=30, max_len=61):
    # Set the length of the fiber to a random integer between 20 and 30
    fiber_length = np.random.randint(min_len, max_len)
    
    # Set the starting point to a random x,y coordinate between (0,0) and (512,512)
    start_point = np.random.randint(start, end, size=2)
    
    # Generate a random angle between 0 and 2*pi
    angle = np.random.uniform(0, 2*np.pi)
    
    # Generate an array of x-coordinates and y-coordinates, evenly spaced along the line
    x_coords = np.linspace(start_point[0], start_point[0] + fiber_length*np.cos(angle), fiber_length)
    y_coords = np.linspace(start_point[1], start_point[1] + fiber_length*np.sin(angle), fiber_length)
    
    # Clip the coordinates to make sure they don't go below 0 or above 512
    x_coords = np.clip(x_coords, 0, 512)
    y_coords = np.clip(y_coords, 0, 512)
    
    # Combine the x- and y-coordinates into a 2D numpy array of shape (fiber_length, 2)
    fiber_coords = np.column_stack((x_coords, y_coords))
    
    return fiber_coords

def generate_fibers(num_of_fibers, start=0, end=513, min_len=30, max_len=61):
    # Initialize an empty list to store the fibers
    fibers = []
    
    # Generate the specified number of fibers and append them to the list
    for i in range(num_of_fibers):
        fiber = generate_fiber(start, end, min_len, max_len)
        fibers.append(fiber)
    
    return fibers

def get_test_fibers_widths(num_of_fibers):
    return np.random.randint(4, 8, size=num_of_fibers)

def get_test_fibers_lengths(num_of_fibers):
    return np.random.randint(30, 70, size=num_of_fibers)

def get_test_fiber_lengths_from_fibers(fibers):
    return np.array([len(fiber) for fiber in fibers])

def get_test_fibers_angles(num_of_fibers):
    return np.random.randint(1,10, size=num_of_fibers) / 10

