class ShortTermMemory:
    def __init__(self, max_items: int = 50):
        self.store = []
        self.max_items = max_items

    def add(self, item):
        self.store.append(item)
        if len(self.store) > self.max_items:
            self.store.pop(0)

    def get_all(self):
        return list(self.store)
