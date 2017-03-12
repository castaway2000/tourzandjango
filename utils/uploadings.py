def upload_path_handler_tour(instance, filename):
    return "tour_%s/%s" % (instance.id, filename)


def upload_path_handler_tour_images(instance, filename):
    return "tour_%s/%s" % (instance.tour.id, filename)