import uuid
from random import randint

def random_string_creating():
    slug = "%s%s" % (str(uuid.uuid4()), randint(0,1000))
    return slug