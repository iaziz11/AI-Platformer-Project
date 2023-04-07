import random


class RandomHashSet():
    def __init__(self) -> None:
        self._set = set()
        self._data = []

    def contains(self, a):
        return a in self._set

    def random_element(self):
        if self.size() > 0:
            return self._data[random.randrange(0, len(self._data))]
        return None

    def size(self):
        return len(self._data)

    def add(self, a):
        if not self.contains(a):
            self._set.add(a)
            self._data.append(a)

    def clear(self):
        self._set.clear()
        self._data.clear()

    def get_object(self, i):
        if i >= self.size():
            raise Exception("Index out of range")

        return self._data[i]

    def get_index(self, a):
        return self._data.index(a)

    def remove_index(self, i):
        if i < 0 or i >= self.size():
            raise Exception("Index out of range")
        self._set.remove(self._data[i])
        self._data.remove(self._data[i])

    def remove_object(self, a):
        self._set.remove(a)
        self._data.remove(a)

    def getData(self):
        return self._data

    def add_sorted(self, a):
        if self.contains(a):
            return
        if self.size() == 0:
            self.add(a)
        else:
            for i in range(self.size()):
                if a.getInnovationNum() < self.get_object(i).getInnovationNum():
                    self._data.insert(i, a)
                    self._set.add(a)
                    return
            self.add(a)
