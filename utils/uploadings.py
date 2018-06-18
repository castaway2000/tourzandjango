def upload_path_handler_city(instance, filename):
    if instance.name:
        return "locations/cities/%s_%s" % (instance.name, filename)
    else:
        return "locations/cities/%s" % (filename)


def upload_path_handler_tour(instance, filename):
    return "tours/original_size%s" % (filename)


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


def upload_path_handler_guide_image(instance, filename):
    return "users/%s/guide/profile_image/%s" % (instance.guide.user.id, filename)


def upload_path_handler_guide_header_images(instance, filename):
    return "users/%s/guide/header_images/%s" % (instance.user.id, filename)


def upload_path_handler_guide_profile_image(instance, filename):
    return "users/%s/guide/profile_image/%s" % (instance.user.id, filename)


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


