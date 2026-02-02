class BaseInMemoryRepository[Key, Type]:

    def __init__(self):
        self._storage: dict[Key, Type] = {}

    def clear(self) -> None:
        self._storage.clear()
