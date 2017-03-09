from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


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