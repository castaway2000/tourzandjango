from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import base64
from django.core.files.base import ContentFile
from .models import *
from .forms import *
import requests
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tourzan.settings import ONFIDO_TOKEN_TEST


@login_required()
def identity_verification_router(request):
    """
    This is a kind of routing view. Depending on already done scan docs uploading of live photo making, the script
    will redirect a user to the needed page.
    However all of 2 verification pages can be directly accessible as well
    """
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
    identity_verification = IdentityVerificationApplicant.objects.filter(general_profile=general_profile).exists()

    if not document_scan:
        return HttpResponseRedirect(reverse("identity_verification_ID_uploading"))
    elif not identity_verification:
        return HttpResponseRedirect(reverse("identity_verification_photo"))
    else:
        return render(request, 'verifications/profile_identity_verification.html', locals())


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
    return render(request, 'verifications/profile_identity_verification_ID_uploading.html', locals())


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

        token = "Token token=%s" % ONFIDO_TOKEN_TEST
        headers = {'Authorization': token}

        #applicant creation
        try:
            applicant = IdentityVerificationApplicant.objects.get(general_profile=general_profile)
        except:
            url = "https://api.onfido.com/v2/applicants"
            applicant_data = {
                "first_name": guide.name,
                "last_name": guide.name
            }
            r = requests.post(url, data=applicant_data, headers=headers)
            result = r.json()
            applicant = IdentityVerificationApplicant.objects.create(general_profile=general_profile,
                                                         applicant_id=result["id"],
                                                         applicant_url=result["href"]
                                                         )

        #sending ID document scan
        #improve this later if it is needed to allow to send several files (for example scans of 2 pages of passport)
        last_doc = DocumentScan.objects.filter(general_profile=general_profile).last()
        url = "https://api.onfido.com/v2/applicants/%s/documents" % applicant.applicant_id
        f = last_doc.file.file
        f.open(mode='rb')
        files = {'file': f}
        r = requests.post(url, files=files,  data={"type": "unknown"})
        f.close()#closing file after a call with it

        #live photo uploading
        url = "https://api.onfido.com/v2/live_photos"
        f = general_profile.webcam_image.file
        f.open(mode='rb')
        files = {'file': f}
        r = requests.post(url, files=files, data={"applicant_id": applicant.applicant_id})
        f.close()#closing file after a call with it

        #creating check and saving check link
        url = "https://api.onfido.com/v2/applicants/%s/checks" % applicant.applicant_id
            #if there is any existing check
        r = requests.get(url, headers=headers)
        result = r.json()
        print(result)

        #A little bit workaround solution but it solves possible bottle necks while testing
        #if there is any existing not finsished check for this applicant - use it.
        previous_check_is_found = False
        if "checks" in result:
            for item in result["checks"]:
                if item["status"] == "in_progress":
                    check_id = item["id"]
                    check, created = IdentityVerificationCheck.objects.update_or_create(check_id=check_id,
                                                                                         applicant = applicant,
                                                                                         defaults={
                                                                                             "check_id": item["id"],
                                                                                             "check_url": item["href"]
                                                                                         })
                    previous_check_is_found = True
                    break

        if not previous_check_is_found:#create new check
            check_data = {
                "type": "express",
                "reports[][name]": "identity",#free available for sandbox
                "reports[][name]": "document",
                "reports[][name]": "facial_similarity"
            }
            r = requests.post(url, data=check_data, headers=headers)
            result = r.json()
            check = IdentityVerificationCheck.objects.create(applicant=applicant,
                                                             check_id=result["id"],
                                                             check_url=result["href"]
                                                             )


        #a call to get full info (not just ids) for the created reports
        url = "https://api.onfido.com/v2/checks/%s/reports" % check.check_id
        r = requests.get(url, headers=headers)
        result = r.json()
        reports = result["reports"]

        #saving information about created reports for the recently created check
        print("reports: %s" % reports)
        for report in reports:
            report_url = "https://api.onfido.com/v2/checks/%s/reports/%s" % (check.check_id, report["id"])
            report_type, created = VerificationReportType.objects.get_or_create(name=report["name"])
            report_status = report["status"]

            defaults_kwargs = dict()
            if report_status:
                report_status, created = VerificationReportStatus.objects.get_or_create(name=report_status)
                defaults_kwargs["status"] = report_status
            report_result = report["result"]
            if report_result:
                report_result, created = VerificationReportResult.objects.get_or_create(name=report_result)
                defaults_kwargs["result"] = report_result
            IdentityVerificationReport.objects.update_or_create(identification_checking=check,
                                                      report_id=report["id"],
                                                      report_url=report_url,
                                                      type=report_type, defaults = defaults_kwargs
                                                      )
        return HttpResponseRedirect(reverse("identity_verification_router"))
    else:
        return render(request, 'verifications/profile_identity_verification_photo.html', locals())