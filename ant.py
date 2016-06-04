from random import uniform


class Ant:
    def __init__(self, v):
        self.__v = uniform(0, v)
        self.__loaded = False
        self.__attribute = None

    def load(self, attribute):
        if self.is_loaded():
            raise Exception("Ant is already loaded!")
        self.__attribute = attribute
        self.__loaded = True

    def is_loaded(self):
        return self.__loaded
