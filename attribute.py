class Attribute:
    """ Simple bean class for coordinates that holds additional information about index and label."""
    def __init__(self, index, coordinates):
        """
        Creates new instance of Attribute.
        :param index: original arff index of row.
        :param coordinates: coordinates of related point
        """
        self.__coordinates = coordinates
        self.__index = index
        self.__label = None
        self.__index = index

    @property
    def get_index(self):
        return self.__index

    @property
    def get_coordinates(self):
        return self.__coordinates

    @property
    def get_label(self):
        return self.__label

    def set_label(self, label):
        self.__label = label

    def is_labeled(self):
        """
        :return: true, if attribute is labeled, otherwise false
        """
        return self.__label is not None
