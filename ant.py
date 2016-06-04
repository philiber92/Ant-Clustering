from random import uniform


class Ant:
    def __init__(self, v):
        self.__v = uniform(0, v)
        self.__loaded = False
        self.__attribute = None

    def load(self, attribute):
        if self.is_loaded:
            raise Exception("Ant is already loaded!")
        self.__attribute = attribute
        self.__loaded = True

    def unload(self):
        if not self.is_loaded:
            raise Exception("Ant isn't currently loaded!")
        self.__attribute = None
        self.__loaded = False

    @property
    def is_loaded(self):
        return self.__loaded

    def get_attribute(self):
        if not self.is_loaded:
            raise Exception("Ant isn't loaded!")
        return self.__attribute

    def get_coordinates(self):
        attr = self.get_attribute()
        return attr.get_coordinates

    @property
    def get_speed(self):
        return self.__v
