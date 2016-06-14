from grid_point import GridPoint
from random import randint
from attribute import Attribute
from ant import Ant


class Grid:
    """
    Represents a 2d pane that provides opportunity to run cluster optimization.
    """
    def __init__(self, x, y, threshold, random_limit=100):
        """
        Creates new Grid class.
        :param x: max x value
        :param y: max y value
        :param threshold: threshold for picking up data
        :param random_limit: max placing attempts until exception is raised
        :return:
        """
        self.__x = x
        self.__y = y
        self.__threshold = threshold
        self.__random_limit = random_limit
        self.__dict = {}

    def place(self, point, item):
        """
        Stores item to given location.
        :param point: store location
        :param item: item to be stored
        """
        self.__check_coordinates(point)
        if self.is_occupied(point):
            raise Exception(str(point) + "Is already occupied!")
        else:
            self.__dict[point] = item

    def place_randomly(self, item):
        """
        Tries to find random location that isn't occupied currently. If it's impossible to find
        a location in given random_limit, a exception is raised. To fix this error, try to expand
        the grid.
        :param item: item to be stored
        :return: none
        """
        for i in range(0, self.__random_limit):
            x = randint(0, self.__x)
            y = randint(0, self.__y)
            point = GridPoint(x, y)
            if not self.is_occupied(point):
                self.place(point, item)
                return
        raise Exception("Couldn't found any free space within " + str(self.__random_limit) + " steps!")

    def pop(self, point):
        """
        Removes specified point from grid. Raises exception if point isn't stored so far.
        :param point: point to be fetched.
        """
        if not self.is_occupied(point):
            raise Exception(str(point) + "isn't set!")
        else:
            self.__dict.pop(point)

    def is_occupied(self, point):
        """
        Checks if point is set.
        :param point: desired location
        :return: true, if point is occupied, otherwise false
        """
        return self.__dict.get(point) is not None

    def __check_coordinates(self, point):
        """
        Checks if specified point satisfies criteria.
        :param point: point need to be tested
        :return: none
        """
        if point.get_x < 0 or point.get_x > self.__x:
            raise Exception("Invalid argument! X is too big or negative!")
        if point.get_y < 0 or point.get_y > self.__y:
            raise Exception("Invalid argument! Y is too big or negative!")

    def get_free_attribute(self):
        """
        Returns a random selected, not picked up attribute. Raises an exception, if all attributes are picked up.
        Try to fix it by increasing number of ants.
        :return: attribute
        """
        items = self.__dict.items()
        attributes = filter(lambda x: isinstance(x[1], Attribute), items)
        size = len(attributes)
        if size == 0:
            raise Exception("Couldn't found any free attribute!")
        random = randint(0, size - 1)
        return attributes[random]

    def get_neighbors(self, point):
        """
        Returns list containing all neighbors of specified point.
        :param point:
        :return: all neighbors of point
        """
        items = self.__dict.items()
        min_x = point.get_x - self.__threshold if (point.get_x - self.__threshold) > 0 else 0
        max_x = point.get_x + self.__threshold if (point.get_x + self.__threshold) < self.__x else self.__x
        min_y = point.get_y - self.__threshold if (point.get_y - self.__threshold) > 0 else 0
        max_y = point.get_y + self.__threshold if (point.get_y + self.__threshold) < self.__y else self.__y
        neighbors = filter(lambda x: x[0] != point and self.__within_distance(x, min_x, max_x, min_y, max_y), items)
        return neighbors

    def __within_distance(self, item, min_x, max_x, min_y, max_y):
        """
        Checks if item is within specified distance.
        :param item: item to be checked
        :param min_x: min x coordinate
        :param max_x: max x coordinate
        :param min_y: min y coordinate
        :param max_y: max y coordinate
        :return: true, if item is within distance, otherwise false
        """
        if item[0].get_x < min_x or item[0].get_x > max_x:
            return False
        if item[0].get_y < min_y or item[0].get_y > max_y:
            return False
        return True

    def drop_all(self):
        """
        Drops all attributes that are picked up currently.
        """
        items = self.__dict.items()
        ants = filter(lambda x: isinstance(x[1], Ant), items)
        for ant in ants:
            self.pop(ant[0])
            self.place(ant[0], ant[1].get_attribute())

    def get_all_items(self):
        """
        :return: all stored items
        """
        return self.__dict.items()

    def get_location(self, item):
        """
        Returns location of item. Raises an exception, if item isn't stored.
        :param item: item to be checked
        :return: location of item
        """
        for key, data in self.__dict.iteritems():
            if item == data:
                return key
        raise Exception("Grid doesn't contain " + str(item))

