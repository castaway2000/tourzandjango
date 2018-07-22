import uuid
from random import randint
import os
from PIL import Image


def random_string_creating():
    slug = "%s%s" % (str(uuid.uuid4()), randint(0,1000))
    return slug


def uuid_creating():
    return uuid.uuid4().hex


def uuid_size_6_creating():
    return uuid.uuid4().hex[:6]


def remove_zeros_from_float(x):
    if (x * 10) % 10 == 0:
        x = int(x)
        return x
    else:
        return x
