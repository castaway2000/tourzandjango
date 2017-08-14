def upload_path_handler_city(instance, filename):
    return "locations/cities/%s/%s" % (instance.id, filename)


def upload_path_handler_tour(instance, filename):
    return "tours/%s/%s" % (instance.id, filename)


def upload_path_handler_tour_images(instance, filename):
    if type(instance).__name__ == "TourImage":
        return "tours/%s/%s" % (instance.tour.id, filename)
    else:
        #not clear for what cases
        return "tours_else/%s/%s" % (instance.id, filename)


def upload_path_handler_blog(instance, filename):
    return "blog_posts/%s/%s" % (instance.id, filename)


def upload_path_handler_user_scanned_docs(instance, filename):
    return "users/%s/docs/%s" % (instance.general_profile.user.id, filename)


def upload_path_handler_guide_header_images(instance, filename):
    return "users/%s/guide/header_images/%s" % (instance.user.id, filename)


def upload_path_handler_guide_profile_image(instance, filename):
    return "users/%s/guide/profile_image/%s" % (instance.user.id, filename)


def upload_path_handler_guide_optional_image(instance, filename):
    return "users/%s/guide/optional_image/%s" % (instance.user.id, filename)


def upload_path_handler_tourist_profile_image(instance, filename):
    return "users/%s/tourist/profile/%s" % (instance.user.id, filename)


def upload_path_handler_tourist_travel_pictures(instance, filename):
    return "users/%s/tourist/travel_pictures/%s" % (instance.user.id, filename)


