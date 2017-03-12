from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Tour


def tours(request):
    return HttpResponse()


def guide_tours(request, username):
    user = request.user
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponseRedirect(reverse("home"))

    #if no username is specified in url, it is possible to display info just for current user
    elif not user.is_anonymous():
        user = request.user
    else:
        return HttpResponseRedirect(reverse("home"))

    context = {

    }
    return render(request, 'tours/guide_tours.html', context)


def tour(request, slug):
    tour = Tour.objects.get(slug=slug)
    guide = tour.guide
    tours_images = tour.tourimage_set.filter(is_active=True).order_by('-is_main', 'id')
    reviews = tour.review_set.filter(is_active=True)

    other_tours = guide.tour_set.filter(is_active=True).exclude(id=tour.id)

    return render(request, 'tours/tour.html', locals())