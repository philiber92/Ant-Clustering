class GridPoint:
    def __init__(self, x, y):
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

