import matplotlib.pyplot as plt
import random


class Plotter:
    """ Simple plotter class that prints first and second coordinate to 2d diagram. """
    def __init__(self, attributes, style):
        """
        Creates new instance of plotter.
        :param attributes: all clustered attributes
        :param style: select marker, e.g. 'o' for circle
        """
        self.__attributes = attributes
        self.__colors = dict()
        self.__style = style

    def __generate_color(self, label):
        """
        Generates a random hex color code.
        :param label: current label of attribute
        :return: hex color code
        """
        color_code = '#'.join([random.choice('0123456789ABCDEF') for x in range(6)])
        self.__colors[label] = '#'.join(color_code)

    def plot(self):
        """
        Plots all attribute coordinates to diagram colored by related label.
        """
        plt.ioff()
        for attr in self.__attributes:
            if attr.get_label not in self.__colors:
                self.__generate_color(attr.get_label)
            self.__plot_attribute(attr)

    def __plot_attribute(self, attr):
        """
        Plots specified attribute to 2d diagram.
        :param attr: attribute to be plotted
        """
        plt.plot(attr.get_coordinates[0], attr.get_coordinates[1], c=self.__colors[attr.get_label], marker=self.__style)

    def show(self):
        """
        Opens window and displays current 2d diagram.
        """
        plt.show()

    def save(self, filename):
        """
        Saves current 2d diagram to specified location.
        :param filename: file of type png or jpg
        """
        plt.savefig(filename)
