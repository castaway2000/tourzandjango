import uuid
from random import randint


def random_string_creating():
    slug = "%s%s" % (str(uuid.uuid4()), randint(0,1000))
    return slug


def uuid_creating():
    random_string = uuid.uuid4()
    return random_string.hex