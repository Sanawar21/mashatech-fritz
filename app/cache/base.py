import json


class BaseCache:
    def __init__(self, path) -> None:
        self.path = path
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.__load_data()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.save()

    def __load_data(self):
        try:
            with open(self.path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self):
        with open(self.path, 'w') as file:
            json.dump(self._data, file, indent=4)

    def create(self, data):
        self.data.append(data)
        self.save()

    def read(self, key_to_check, value):
        for item in self.data:
            if item[key_to_check] == value:
                return item
        return None

    def update(self, key_to_update, value, new_data):
        for item in self.data:
            if item[key_to_update] == value:
                item.update(new_data)
                break
        self.save()

    def delete(self, key_to_check, value):
        self.data = [item for item in self.data if item[key_to_check] != value]

    def clear_data(self):
        self.data = []
