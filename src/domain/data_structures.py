from collections import deque
import time
import hashlib

class CircularBuffer:
    """
    Maintains a fixed-size window of recent transactions.
    Demonstrates: Efficient memory management for streaming data.
    """
    def __init__(self, size: int):
        self.buffer = deque(maxlen=size)

    def add(self, amount: float):
        self.buffer.append((time.time(), amount))

    def get_velocity(self, window_seconds: int) -> float:
        current_time = time.time()
        return sum(amt for ts, amt in self.buffer if current_time - ts <= window_seconds)

class IPBlacklistTrie:
    """
    Prefix-based matching for IP blacklisting.
    Demonstrates: O(L) lookup complexity vs O(N) list search.
    """
    def __init__(self):
        self.root = {}

    def insert(self, ip: str):
        node = self.root
        for part in ip.split('.'):
            if part not in node:
                node[part] = {}
            node = node[part]
        node['*'] = True 

    def is_blacklisted(self, ip: str) -> bool:
        node = self.root
        for part in ip.split('.'):
            if part not in node:
                return False
            node = node[part]
            if '*' in node:
                return True
        return False

class HyperLogLog:
    """
    Cardinality estimator for unique user tracking.
    Demonstrates: Probabilistic data structures for massive scale.
    """
    def __init__(self, b=10):
        self.b = b
        self.m = 1 << b 
        self.registers = [0] * self.m

    def _hash(self, item):
        return int(hashlib.sha1(str(item).encode('utf8')).hexdigest(), 16)

    def add(self, item):
        x = self._hash(item)
        idx = x & (self.m - 1)
        w = x >> self.b
        rho = (bin(w).split('1')[-1].count('0') + 1) if w > 0 else 64 - self.b
        self.registers[idx] = max(self.registers[idx], rho)

    def count(self) -> int:
        alpha_m = 0.7213 / (1 + 1.079 / self.m)
        estimate = alpha_m * (self.m ** 2) / sum([2.0**-r for r in self.registers])
        return int(estimate)