import arff
import codecs
import numpy as np


class ArffParser:
    def __init__(self, filename):
        file_ = codecs.open(filename, 'rb', 'utf-8')
        self.__data = arff.load(file_)

    def __iter__(self):
        return ArffParserIter(self.__data['data'])

    def get_data(self):
        return self.__data['data']

    def get_data_matrix(self):
        return np.matrix(self.__data['data'])

    def count_dimensions(self):
        # using of class labels is forbidden
        return len(self.__data[0]) - 1


class ArffParserIter:
    def __init__(self, data):
        self.__data = data
        self.__i = 0
        self.__max = len(data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.__i < self.__max:
            curr_data = self.__data[self.__i]
            self.__i += 1
            return curr_data[:-1]
        else:
            raise StopIteration()
