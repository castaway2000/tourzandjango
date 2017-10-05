from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import base64
from django.core.files.base import ContentFile
from .models import *
from .forms import *
import requests
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required()
def identity_verification(request):
    page = "identity_verification"
    #remake this to decorator
    user = request.user
    general_profile = user.generalprofile
    try:
        guide = user.guideprofile
        if not guide.uuid:
            guide.save(force_update=True)#this will populate automatically uuid value if it is empty so far
    except:
        messages.error(request, 'You have no permissions for this action!')
        return render(request, 'users/home.html', locals())

    document_scan = DocumentScan.objects.filter(general_profile=general_profile).exists()
    identity_verification = IdentityVerification.objects.filter(general_profile=general_profile).exists()

    if not document_scan:
        return HttpResponseRedirect(reverse("identity_verification_ID_uploading"))
    elif not general_profile.webcam_image:
        return HttpResponseRedirect(reverse("identity_verification_photo"))
    else:
        return render(request, 'users/profile_identity_verification.html', locals())


@login_required()
def identity_verification_ID_uploading(request):
    page = "identity_verification"

    #remake this to decorator
    user = request.user
    try:
        guide = user.guideprofile
        if not guide.uuid:
            guide.save(force_update=True)#this will populate automatically uuid value if it is empty so far
    except:
        messages.error(request, 'You have no permissions for this action!')
        return render(request, 'users/home.html', locals())

    document_uploaded = user.generalprofile.documentscan_set.filter(is_active=True).last()#approved
    docs_form = DocsUploadingForm(request.POST or None, request.FILES or None)

    general_profile = user.generalprofile
    if request.POST:
        #documents uploading section
        if not document_uploaded or document_uploaded.status_id == 3:#not presented or rejected
            if docs_form.is_valid():

                #ADD some validation here for file size and extension
                if request.FILES.get("file"):
                    count = 0
                    for file in request.FILES.getlist("file"):
                        if count < 5:#uploading not more than 5 files
                            DocumentScan.objects.create(file=file, general_profile=general_profile)
                            count += 1
                        else:
                            break

                    if count == 1:
                        messages.success(request, 'File was successfully uploaded!')
                    else:
                        messages.success(request, 'Files were successfully uploaded!')

                    #retrieve docs afrer uploading
                    is_just_uploaded = True
    return render(request, 'users/profile_identity_verification_ID_uploading.html', locals())


@login_required()
def identity_verification_photo(request):
    page = "identity_verification"

    #remake this to decorator
    user = request.user
    try:
        guide = user.guideprofile
        if not guide.uuid:
            guide.save(force_update=True)#this will populate automatically uuid value if it is empty so far
    except:
        messages.error(request, 'You have no permissions for this action!')
        return render(request, 'users/home.html', locals())

    general_profile = user.generalprofile
    if request.POST:
        webcam_img = request.POST.get("webcam_image")
        format, imgstr = webcam_img.split(';base64,')
        ext = format.split('/')[-1]
        webcam_img_file = ContentFile(base64.b64decode(imgstr), name='webcam.' + ext)
        general_profile.webcam_image = webcam_img_file
        general_profile.save(force_update=True)
        request.session["identification_step"] = 2

        # test_tLlvRsGwFHHBHZr_mw02f372SkQwFAb3
        # Authorization: Token token=your_api_token
        headers = {'Authorization': 'Token token=test_tLlvRsGwFHHBHZr_mw02f372SkQwFAb3'}
        url = "https://api.onfido.com/v2/applicants"
        applicant_data = {
            "first_name": "Alex"
        }
        r = requests.post(url, data=applicant_data, headers=headers)
        result = r.json()

        return HttpResponseRedirect(reverse("identity_verification"))

    if not general_profile.is_verified:
        if not request.session.get("identification_step") or request.session.get("identification_step")==1:
            request.session["identification_step"] = 1
            return render(request, 'users/profile_identification_step1.html', locals())
        elif request.session["identification_step"] == 2:

            headers = {'Authorization': 'Token token=test_tLlvRsGwFHHBHZr_mw02f372SkQwFAb3'}
            # url = "https://api.onfido.com/v2/applicants"
            # applicant_data = {
            #     "first_name": "Alex",
            #     "last_name": "Terentyev"
            # }
            # r = requests.post(url, data=applicant_data, headers=headers)
            # result = r.json()
            # print(result)
            # guide.onfido_id = result["id"]
            # guide.save(force_update=True)

            # url = "https://api.onfido.com/v2/applicants/%s/checks" % guide.onfido_id
            # check_data = {
            #     "type": "express",
            #     "reports[][name]": "identity"
            # }
            # r = requests.post(url, data=check_data, headers=headers)
            # result = r.json()
            # print(result)

            url = "https://api.onfido.com/v2/checks/c754bfc5-110a-4632-8b03-87de2dd880c6/reports/9d621e6c-8734-4848-b2cc-4e367a5151d5"
            r = requests.get(url, headers=headers)
            result = r.json()
            # print(result)

            return render(request, 'users/profile_identity_verification_photo.html', locals())
    else:
        return HttpResponseRedirect(reverse("general_settings"))