import sys
import math
import numpy as np
from arff_parser import ArffParser
from grid import Grid
from attribute import Attribute
from ant import Ant
from random import uniform


class AntClustering:
    """ Clustering optimization using Ant Colony Clustering Algorithm."""
    def __init__(self, data, n, m, s, a, c, v, x, y):
        self.__ant_size = n
        self.__runs = m
        self.__threshold = s
        self.__alpha = a
        self.__c = c
        self.__max_speed = v
        self.__min_neighbors = 2
        self.__init_grid(data, x, y)
        self.__init_ants(v)
        self.__label_class = 1

    def __init_grid(self, data, x, y):
        """
        Creates new grid.
        :param data: data to be placed on grid
        :param x: max x
        :param y: max y
        """
        self.__grid = Grid(x, y, self.__threshold)
        i = 0
        for coordinates in data:
            self.__grid.place_randomly(Attribute(i, np.asarray(coordinates)))
            i += 1

    def __init_ants(self, v):
        """
        Creates specified number of ants by random velocity.
        :param v: max velocity
        """
        self.__ants = []
        for i in range(0, self.__ant_size):
            self.__ants.append(Ant(v))

    def __load_all(self):
        """
        Loads each ant by one random selected attribute.
        """
        for ant in self.__ants:
            if not ant.is_loaded:
                attr_item = self.__grid.get_free_attribute()
                ant.load(attr_item[1])
                self.__grid.pop(attr_item[0])
                self.__grid.place(attr_item[0], ant)

    def __pick(self, ant):
        """
        Checks if ant needs to pick up attribute. Otherwise it moves to new random location.
        :param ant: current ant
        """
        attr_item = self.__grid.get_free_attribute()
        if self.__prob_pick(ant, attr_item) > uniform(0, 1):
            ant.load(attr_item[1])
            self.__grid.place_randomly(ant)
            self.__grid.pop(attr_item[0])

    def __drop(self, ant):
        """
        Checks if ant needs to drop off attribute. Otherwise it moves to new random location.
        :param ant: current ant
        """
        current_location = self.__grid.get_location(ant)
        if self.__prob_drop(ant, current_location) > uniform(0, 1):
            self.__grid.pop(current_location)
            self.__grid.place(current_location, ant.get_attribute())
            ant.unload()
        else:
            self.__grid.place_randomly(ant)
            self.__grid.pop(current_location)

    def cluster(self):
        """
        Runs clustering optimization.
        """
        self.__load_all()
        for i in range(0, self.__runs):
            for ant in self.__ants:
                if ant.is_loaded:
                    self.__drop(ant)
                else:
                    self.__pick(ant)
        self.__grid.drop_all()
        self.__set_labels()
        self.__get_labels()

    def __get_labels(self):
        items = self.__grid.get_all_items()
        sorted_items = sorted(items, key=lambda x: x[1].get_label)
        for item in sorted_items:
            print(item[1].get_label)

    def __set_labels(self):
        """
        Labels all neighbors within given max distance by one marker. Outliners gets own markers.
        """
        # that's really bad :/
        items = self.__grid.get_all_items()
        for item in items:
            if not item[1].is_labeled():
                self.__set_label(item)

    def __set_label(self, item):
        if item[1].is_labeled():
            return
        neighbors = self.__grid.get_neighbors(item[0])
        if len(neighbors) < self.__min_neighbors:
            item[1].set_label(self.__label_class)
            self.__label_class += 1
        else:
            labeled_neighbors = filter(lambda x: x[1].is_labeled(), neighbors)
            if len(labeled_neighbors) > 0:
                item[1].set_label(labeled_neighbors[0][1].get_label)
            else:
                item[1].set_label(self.__label_class)
                self.__label_class += 1
        for neighbor in neighbors:
            self.__set_label(neighbor)

    def __average_similarity(self, ant, point, attr):
        """
        Function that calculates ration of neighbors and current ant. It's necessary to compute dropping/picking
        probability.
        :param ant: current ant
        :param point: current location
        :param attr: attribute need to be checked
        :return: ratio
        """
        neighbors = self.__grid.get_neighbors(point)
        distances = 0
        for neighbor in neighbors:
            v2 = neighbor[1].get_coordinates if isinstance(neighbor[1], Attribute) else neighbor[1].get_coordinates()
            dist = np.linalg.norm(attr.get_coordinates - v2)
            distances += 1 - dist / (self.__alpha * (1 + (ant.get_speed - 1) / self.__max_speed))
        return max(0, (1 / pow(self.__threshold, 2)) * distances)

    def __prob_drop(self, ant, point):
        """
        Calculates probability to drop off attribute picked up by ant.
        :param ant: current ant
        :param attr_item: picked up attribute
        :return: dropping probability
        """
        average_sim = self.__average_similarity(ant, point, ant.get_attribute())
        return self.__sigmoid(average_sim)

    def __prob_pick(self, ant, attr_item):
        """
        Calculates probability to pick up attribute by ant.
        :param ant: current ant
        :param attr_item: attribute
        :return: picking probability
        """
        average_sim = self.__average_similarity(ant, attr_item[0], attr_item[1])
        return 1 - self.__sigmoid(average_sim)

    def __sigmoid(self, x):
        """
        Sigmoid function used as probability conversion function.
        :param x: average similarity
        :return: sigmoid
        """
        exp = math.exp(self.__c * x)
        return (1 - exp) / (1 + exp)


if __name__ == "__main__":
    print(sys.argv[1])
    parser = ArffParser(sys.argv[1])
    clustering = AntClustering(parser.get_data_matrix(), int(sys.argv[2]), int(sys.argv[3]),
                               float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]),
                               int(sys.argv[8]), int(sys.argv[9]))
    clustering.cluster()
