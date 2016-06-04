from grid_point import GridPoint
from random import randint


class Grid:
    def __init__(self, x, y, threshold, random_limit=100):
        self.__x = x
        self.__y = y
        self.__threshold = threshold
        self.__random_limit = random_limit
        self.__dict = {}

    def place(self, point, item):
        self.__check_coordinates(point)
        if self.is_occupied(point):
            raise Exception(str(point) + "Is already occupied!")
        else:
            self.__dict[point] = item

    def place_randomly(self, item):
        for i in range(1, self.__random_limit):
            x = randint(0, self.__x)
            y = randint(0, self.__y)
            point = GridPoint(x, y)
            if not self.is_occupied(point):
                self.place(point, item)
                return
        raise Exception("Couldn't found any free space within " + str(self.__random_limit) + " steps!")

    def pop(self, point):
        if not self.is_occupied(point):
            raise Exception(str(point) + "isn't set!")
        else:
            self.__dict.pop(point)

    def is_occupied(self, point):
        return self.__dict.get(point) is not None

    def __check_coordinates(self, point):
        if point.get_x < 0 or point.get_x > self.__x:
            raise Exception("Invalid argument! X is too big or negative!")
        if point.get_y < 0 or point.get_y > self.__y:
            raise Exception("Invalid argument! Y is too big or negative!")
