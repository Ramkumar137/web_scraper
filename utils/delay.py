import random
import time

MIN_DELAY = 5
MAX_DELAY = 12

def polite_sleep():
    sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"💤 Sleeping {sleep_time:.2f}s")
    time.sleep(sleep_time)
