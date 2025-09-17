# SuperFastPython.com
# example of executing a target task function in a separate thread
from time import sleep
from threading import Thread
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
 
# a simple task that blocks for a moment and prints a message
def subscore_1():
    sleep(2)
    return 1

def subscore_2():
    sleep(8)
    return 1

def subscore_3():
    return 1

def subscore_4():
    return 1

if __name__ == "__main__":
    pool = ThreadPool(processes=10)
    result1 = pool.apply_async(subscore_1)
    print("1")
    result2 = pool.apply_async(subscore_2)
    print("1")
    result3 = pool.apply_async(subscore_3)
    print("1")
    result4 = pool.apply_async(subscore_4)
    print("1")
    value1 = result1.get()
    print("1")
    value2 = result2.get()
    print("1")
    value3 = result3.get()
    print("1")
    value4 = result4.get()
    print("1")
    pool.close()
    print("1")
    print(value1 + value2 + value3 + value4)
    