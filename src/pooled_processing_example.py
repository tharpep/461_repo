from multiprocessing.pool import ThreadPool
from time import sleep


def subscore_1() -> int:
    sleep(2)
    return 1


def subscore_2() -> int:
    sleep(8)
    return 1


def subscore_3() -> int:
    return 1


def subscore_4() -> int:
    return 1


if __name__ == "__main__":
    pool = ThreadPool(processes=10)
    result1 = pool.apply_async(subscore_1)
    result2 = pool.apply_async(subscore_2)
    result3 = pool.apply_async(subscore_3)
    result4 = pool.apply_async(subscore_4)
    value1 = result1.get()
    value2 = result2.get()
    value3 = result3.get()
    value4 = result4.get()
    pool.close()
    print(value1 + value2 + value3 + value4)
