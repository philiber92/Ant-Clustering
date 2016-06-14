class GridPoint:
    """ Simple bean class that is used to represent a point in Grid class. """
    def __init__(self, x, y):
        """
        Creats a new instance of GridPoint.
        :param x: x coordinate
        :param y: y coordinate
        """
        self.__x = x
        self.__y = y

    @property
    def get_x(self):
        return self.__x

    @property
    def get_y(self):
        return self.__y

    def __str__(self):
        return "GridPoint {x: " + str(self.get_x) + ", y: " + str(self.get_y) + "}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.get_x, self.get_y) == (other.get_x, other.get_y)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.get_x, self.get_y))

