import time
import random
from fake_useragent import UserAgent


class RotateUserAgentMiddleware:
    def __init__(self):
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        request.headers["User-Agent"] = self.ua.random


class RequestDelayMiddleware:
    def __init__(self, delay_range=(0.5, 2.0)):
        self.delay_range = delay_range

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
