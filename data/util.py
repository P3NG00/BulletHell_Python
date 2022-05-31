from math import sqrt

"""utility functions"""


def distance(point_1, point_2):
    """returns the distance between two points"""
    return hypotenuse(point_1[0] - point_2[0], point_1[1] - point_2[1])


def hypotenuse(side_1, side_2):
    """returns the hypotenuse of given sides"""
    return sqrt((side_1 ** 2) + (side_2 ** 2))


def normalize(vector):
    """returns a new vector with the same direction but a magnitude of 1"""
    new_vector = vector.copy()
    magnitude = hypotenuse(new_vector[0], new_vector[1])
    # check magnitude is already valid. if 0, return because impossible to scale
    if magnitude == 1.0 or magnitude == 0.0:
        return new_vector
    # scale magnitude to 1
    new_vector[0] /= magnitude
    new_vector[1] /= magnitude
    return new_vector
