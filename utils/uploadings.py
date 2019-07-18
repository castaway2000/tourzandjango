def upload_path_handler_city(instance, filename):
    if instance.name:
        return "locations/cities/%s/%s" % (instance.name, filename)
    else:
        return "locations/cities/%s" % (filename)


def upload_path_handler_city_large(instance, filename):
    if instance.name:
        return "locations/cities/large/%s/%s" % (instance.name, filename)
    else:
        return "locations/cities/large/%s" % (filename)


def upload_path_handler_city_medium(instance, filename):
    if instance.name:
        return "locations/cities/medium/%s/%s" % (instance.name, filename)
    else:
        return "locations/cities/medium/%s" % (filename)


def upload_path_handler_city_small(instance, filename):
    if instance.name:
        return "locations/cities/small/%s/%s" % (instance.name, filename)
    else:
        return "locations/cities/small/%s" % (filename)


def upload_path_handler_country(instance, filename):
    if instance.name:
        return "locations/countries/%s/%s" % (instance.name, filename)
    else:
        return "locations/countries/%s" % (filename)


def upload_path_handler_country_large(instance, filename):
    if instance.name:
        return "locations/countries/large/%s/%s" % (instance.name, filename)
    else:
        return "locations/countries/large/%s" % (filename)


def upload_path_handler_country_medium(instance, filename):
    if instance.name:
        return "locations/countries/medium/%s/%s" % (instance.name, filename)
    else:
        return "locations/countries/medium/%s" % (filename)


def upload_path_handler_country_small(instance, filename):
    if instance.name:
        return "locations/countries/small/%s/%s" % (instance.name, filename)
    else:
        return "locations/countries/small/%s" % (filename)

def upload_path_handler_tour(instance, filename):
    return "tours/original_size/%s" % (filename)

def upload_path_handler_tour_large(instance, filename):
    return "tours/large_size/%s" % (filename)


def upload_path_handler_tour_medium(instance, filename):
    return "tours/medium_size/%s" % (filename)


def upload_path_handler_tour_small(instance, filename):
    return "tours/small_size/%s" % (filename)


def upload_path_handler_tour_images(instance, filename):
    return "tours/%s/%s" % (instance.tour.id, filename)


def upload_path_handler_blog(instance, filename):
    return "blog_posts/%s" % (filename)


def upload_path_handler_user_scanned_docs(instance, filename):
    return "users/%s/docs/%s" % (instance.general_profile.user.id, filename)


def upload_path_handler_guide_answer_image(instance, filename):
    return "users/%s/guide/profile_image/%s" % (instance.guide.user.id, filename)

def upload_path_handler_guide_answer_image_large(instance, filename):
    return "users/%s/guide/profile_image/large_size/%s" % (instance.guide.user.id, filename)

def upload_path_handler_guide_answer_image_medium(instance, filename):
    return "users/%s/guide/profile_image/medium_size/%s" % (instance.guide.user.id, filename)

def upload_path_handler_guide_answer_image_small(instance, filename):
    return "users/%s/guide/profile_image/small_size/%s" % (instance.guide.user.id, filename)

def upload_path_handler_guide_image(instance, filename):
    return "users/%s/guide/profile_image/%s" % (instance.guide.user.id, filename)

def upload_path_handler_guide_header_images(instance, filename):
    return "users/%s/guide/header_images/%s" % (instance.user.id, filename)

def upload_path_handler_guide_profile_image(instance, filename):
    return "users/%s/guide/profile_image/%s" % (instance.user.id, filename)

def upload_path_handler_guide_profile_image_large(instance, filename):
    return "users/%s/guide/profile_image/large/%s" % (instance.user.id, filename)

def upload_path_handler_guide_profile_image_medium(instance, filename):
    return "users/%s/guide/profile_image/medium/%s" % (instance.user.id, filename)

def upload_path_handler_guide_profile_image_small(instance, filename):
    return "users/%s/guide/profile_image/small/%s" % (instance.user.id, filename)


def upload_path_handler_guide_optional_image(instance, filename):
    return "users/%s/guide/optional_image/%s" % (instance.user.id, filename)


def upload_path_handler_guide_license(instance, filename):
    return "users/%s/guide/license/%s" % (instance.user.id, filename)


def upload_path_handler_guide_webcam_image(instance, filename):
    return "users/%s/webcam_images/%s" % (instance.user.id, filename)


def upload_path_handler_tourist_profile_image(instance, filename):
    return "users/%s/tourist/profile/%s" % (instance.user.id, filename)


def upload_path_handler_tourist_travel_pictures(instance, filename):
    return "users/%s/tourist/travel_pictures/%s" % (instance.user.id, filename)


def upload_path_handler_homepage(instance, filename):
    return "homepage/%s" % (filename)


def upload_path_handler_homepage_large(instance, filename):
    return "homepage/large/%s" % (filename)


def upload_path_handler_homepage_medium(instance, filename):
    return "homepage/medium/%s" % (filename)


def upload_path_handler_homepage_small(instance, filename):
    return "homepage/small/%s" % (filename)
