import matplotlib.pyplot as plt
from imageio import imread


def get_image(url):
    image = imread(url)
    return image



