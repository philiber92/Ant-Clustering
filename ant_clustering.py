import sys
import math
import numpy as np
from arff_parser import ArffParser
from grid import Grid
from attribute import Attribute
from ant import Ant
from random import uniform


class AntClustering:
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

    def __init_grid(self, data, x, y):
        self.__grid = Grid(x, y, self.__threshold)
        for coordinates in data:
            attr = Attribute(np.asarray(coordinates[0]))
            self.__grid.place_randomly(Attribute(np.asarray(coordinates)))

    def __init_ants(self, v):
        self.__ants = []
        for i in range(0, self.__ant_size):
            self.__ants.append(Ant(v))

    def __load_all(self):
        for ant in self.__ants:
            if not ant.is_loaded:
                attr_item = self.__grid.get_free_attribute()
                ant.load(attr_item[1])
                self.__grid.pop(attr_item[0])
                self.__grid.place(attr_item[0], ant)

    def __pick(self, ant):
        attr_item = self.__grid.get_free_attribute()
        if self.__prob_pick(ant, attr_item) > uniform(0, 1):
            ant.load(attr_item[1])
            self.__grid.place_randomly(ant)
            self.__grid.pop(attr_item[0])

    def __drop(self, ant):
        current_location = self.__grid.get_location(ant)
        if self.__prob_drop(ant, current_location) > uniform(0, 1):
            self.__grid.pop(current_location)
            self.__grid.place(current_location, ant.get_attribute())
            ant.unload()
        else:
            self.__grid.place_randomly(ant)
            self.__grid.pop(current_location)

    def cluster(self):
        self.__load_all()
        for i in range(0, self.__runs):
            for ant in self.__ants:
                if ant.is_loaded:
                    self.__drop(ant)
                else:
                    self.__pick(ant)
        self.__grid.drop_all()
        self.__set_labels()
        # TODO: add return

    def __set_labels(self):
        # that's really bad :/
        label_class = 0
        items = self.__grid.get_all_items()
        for item in items:
            neighbors = self.__grid.get_neighbors(item[0])
            if len(neighbors) < self.__min_neighbors:
                item[1].set_label = label_class
                label_class += 1
            elif not item[1].is_labeled:
                item[1].set_label = label_class
                for neighbor in neighbors:
                    neighbor[1].set_label = label_class
                label_class += 1

    def __average_similarity(self, ant, point, attr):
        neighbors = self.__grid.get_neighbors(point)
        distances = 0
        for neighbor in neighbors:
            v2 = neighbor[1].get_coordinates if isinstance(neighbor[1], Attribute) else neighbor[1].get_coordinates()
            dist = np.linalg.norm(attr.get_coordinates - v2)
            distances += 1 - dist / (self.__alpha * (1 + (ant.get_speed - 1) / self.__max_speed))
        return max(0, (1 / self.__threshold ^ 2) * distances)

    def __prob_drop(self, ant, point):
        average_sim = self.__average_similarity(ant, point, ant.get_attribute())
        return self.__sigmoid(average_sim)

    def __prob_pick(self, ant, attr_item):
        average_sim = self.__average_similarity(ant, attr_item[0], attr_item[1])
        return 1 - self.__sigmoid(average_sim)

    def __sigmoid(self, x):
        exp = math.exp(self.__c * x)
        return (1 - exp) / (1 + exp)


if __name__ == "__main__":
    parser = ArffParser(sys.argv[0])
    clustering = AntClustering(parser.get_data_matrix(), sys.argv[1], sys.argv[2],
                               sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6],
                               sys.argv[8], sys.argv[7])
    clustering.cluster()
