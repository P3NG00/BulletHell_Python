from math import sqrt

"""utility functions"""


def distance(point_1, point_2):
    """returns the distance between two points"""
    return hypotenuse(point_2[0] - point_1[0], point_2[1] - point_1[1])


def hypotenuse(side_1, side_2):
    """returns the hypotenuse of given sides"""
    return sqrt((side_1 ** 2) + (side_2 ** 2))


def normalize(vector, scaled_magnitude=1.0):
    """returns a new vector with the same direction but a magnitude of 1"""
    new_vector = vector.copy()
    magnitude = hypotenuse(new_vector[0], new_vector[1])
    # check magnitude is already valid. if 0, return because impossible to scale
    if magnitude == scaled_magnitude or magnitude == 0.0:
        return new_vector
    # scale magnitude
    for i in range(2):
        new_vector[i] *= scaled_magnitude / magnitude
    return new_vector


def subtract(vector_1, vector_2):
    """returns the difference between two vectors"""
    return [vector_1[i] - vector_2[i] for i in range(2)]
