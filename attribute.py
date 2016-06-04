class Attribute:
    def __init__(self, coordinates):
        self.__coordinates = coordinates
        self.__label = None

    @property
    def get_coordinates(self):
        return self.__coordinates

    @property
    def get_label(self):
        return self.__label

    def set_label(self, label):
        self.__label = label

    def is_labeled(self):
        return self.__label is not None
