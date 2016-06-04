class Attribute:
    def __init__(self, coordinates):
        self.__coordinates = coordinates

    @property
    def get_coordinates(self):
        return self.__coordinates