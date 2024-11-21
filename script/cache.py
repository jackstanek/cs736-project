
class Cache:

    def __init__(self, capacity):
        self.queue = []
        self.capacity_bytes = capacity
        self.stored_bytes = 0
        self.clients = {}

    def add(self, item):
        bytes = item["key_size"] + item["value_size"]
        if all(item["key"] != d["key"] for d in self.queue):
            self.queue.append(item)
            if not (item["client"] in self.clients):
                self.clients[item["client"]] = 0
            self.clients[item["client"]] += bytes
            self.stored_bytes += bytes

            while self.stored_bytes > self.capacity_bytes:
                pop = self.queue.pop(0)
                pop_bytes = pop["key_size"] + pop["value_size"]
                self.stored_bytes -= pop_bytes
                self.clients[pop["client"]] -= pop_bytes

    def get_state(self):
        return self.clients.copy()
