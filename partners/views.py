from django.shortcuts import render
from .forms import PartnerForm
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .models import IntegrationPartners


# Create your views here.
def api_partner_application(request):
    form = PartnerForm(request.POST or None)
    if request.POST and form.is_valid():
        new_form = form.save(commit=False)
        new_form = form.save()
        request.session["pending_api_application"] = True
        return HttpResponseRedirect(reverse("api_partner_application_success"))

    return render(request, 'partners/api_partner_application.html', locals())


def api_partner_application_success(request):
    pending_api_application = request.session.get("pending_api_application")
    if not pending_api_application:
        return HttpResponseRedirect(reverse("api_partner_application"))
    return render(request, 'partners/api_partner_application_success.html', locals())