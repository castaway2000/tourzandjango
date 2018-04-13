import uuid
from random import randint


def random_string_creating():
    slug = "%s%s" % (str(uuid.uuid4()), randint(0,1000))
    return slug


def uuid_creating():
    return uuid.uuid4().hex


def uuid_size_6():
    return uuid.uuid4().hex[:6].upper()