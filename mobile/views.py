from mobile.models import Waitlist
from django.shortcuts import render


def waitlist(request):
    try:
        name = request.POST['full_name']
        email = request.POST['email']
        city = request.POST['city']
        country = request.POST['country']
        comments = request.POST['comments']
        waitlist = Waitlist.objects.get_or_create(email=email)[0]
        waitlist.name = name
        waitlist.city = city
        waitlist.country = country
        waitlist.comments = comments
        waitlist.save(force_update=True)
    except:
        pass
    return render(request, 'mobile/waitlist.html', locals())
