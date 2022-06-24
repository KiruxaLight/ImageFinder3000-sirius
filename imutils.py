import numpy as np
from PIL import Image
import imagehash
import random
from random import randint
import string
from make_text import make_text_from_image

def get_hash(img: Image):
    hash_image = imagehash.average_hash(img)
    return hash_image

def read_image(name: str):
    img = Image.open(name)
    my_hash = get_hash(img)
    return my_hash

def generate_random_string(length):
    letters = string.ascii_lowercase + ' '
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


def get_text_from_image(path: str):
    return make_text_from_image(path)

import argparse

if __name__ == "__main__":
    get_text_from_image("jelly1.png")