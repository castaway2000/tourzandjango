def upload_path_handler_tour(instance, filename):
    return "tour_%s/%s" % (instance.id, filename)


def upload_path_handler_tour_images(instance, filename):
    if type(instance).__name__ == "TourImage":
        return "tour_%s/%s" % (instance.tour.id, filename)
    else:
        return "tour_%s/%s" % (instance.id, filename)


def upload_path_handler_blog(instance, filename):
    return "blog/blog_%s/%s" % (instance.id, filename)


def upload_path_handler_user_scanned_docs(instance, filename):
    return "users/%s/docs/%s" % (instance.general_profile.user.username, filename)
