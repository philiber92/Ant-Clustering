import sys
from arff_parser import ArffParser
from grid import Grid
from attribute import Attribute


class AntClustering:
    def __init__(self, data, n, m, s, a, c, v, x, y):
        self.__ant_size = n
        self.__runs = m
        self.__threshold = s
        self.__alpha = a
        self.__c = c
        self.__max_speed = v
        self.__init_grid(data, x, y)

    def __init_grid(self, data, x, y):
        self.__grid = Grid(x, y)
        for coordinates in data:
            self.__grid.place_randomly(Attribute(coordinates))

    def __init_ants(self):
        self.__ants = []
        # TODO

if __name__ == "__main__":
    parser = ArffParser(sys.argv[0])
    clustering = AntClustering(parser.get_data_matrix(), sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6],
                               sys.argv[8], sys.argv[7])
