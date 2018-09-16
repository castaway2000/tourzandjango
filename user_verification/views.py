from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import base64
from django.core.files.base import ContentFile
from .models import *
from .forms import *
import requests
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from tourzan.settings import ONFIDO_TOKEN, ONFIDO_IS_TEST_MODE
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import pycountry


@login_required()
@never_cache
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
@never_cache
def identity_verification_ID_uploading(request):
    page = "identity_verification"

    countries = [country.name for country in pycountry.countries]

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
    form = DocsUploadingForm(request.POST or None, request.FILES or None)
    document_types = ["passport", "driving_licence"]

    general_profile = user.generalprofile
    if request.POST:
        #documents uploading section
        if form.is_valid():
            # data = request.POST
            data = request.POST
            general_profile.registration_country = data.get("registration_country")
            general_profile.registration_state = data.get("registration_state")
            general_profile.registration_city = data.get("registration_city")
            general_profile.registration_street = data.get("registration_street")
            general_profile.registration_building_nmb = data.get("registration_building_nmb")
            general_profile.registration_flat_nmb = data.get("registration_flat_nmb")
            general_profile.registration_postcode = data.get("registration_postcode")
            general_profile.save(force_update=True)

            document_type = data.get("document_type")
            document_type, created = DocumentType.objects.get_or_create(name=document_type)

            #ADD some validation here for file size and extension
            if request.FILES.get("file"):
                count = 0
                for file in request.FILES.getlist("file"):
                    if count < 5:#uploading not more than 5 files
                        DocumentScan.objects.create(file=file, general_profile=general_profile,
                                                    document_type=document_type)
                        count += 1
                    else:
                        break

                if count == 1:
                    messages.success(request, 'File was successfully uploaded!')
                else:
                    messages.success(request, 'Files were successfully uploaded!')

            return HttpResponseRedirect(reverse("identity_verification_photo"))
    return render(request, 'verifications/profile_identity_verification_ID_uploading.html', locals())


@login_required()
@never_cache
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
        print(request.POST)
        webcam_img = request.POST.get("webcam_image")
        format, imgstr = webcam_img.split(';base64,')
        ext = format.split('/')[-1]
        webcam_img_file = ContentFile(base64.b64decode(imgstr), name='webcam.' + ext)

        #08032018 temporary workaround solution for cases when there are no first_name and last name on general profile
        if not general_profile.first_name and request.POST.get("first_name"):
            general_profile.first_name = request.POST.get("first_name")
        if not general_profile.last_name and request.POST.get("last_name"):
            general_profile.last_name = request.POST.get("last_name")

        general_profile.webcam_image = webcam_img_file
        general_profile.save(force_update=True)


        token = "Token token=%s" % ONFIDO_TOKEN
        headers = {'Authorization': token}

        #applicant creation
        try:
            applicant = IdentityVerificationApplicant.objects.get(general_profile=general_profile)
            print ("an applicant were retrieved from local db")
        except:
            url = "https://api.onfido.com/v2/applicants"
            applicant_data = {
                "first_name": guide.user.generalprofile.first_name,
                "last_name": guide.user.generalprofile.last_name,
                "email": guide.user.email,
            }
            if guide.date_of_birth:
                applicant_data["dob"] = guide.date_of_birth.strftime('%Y-%m-%d')

            if general_profile.registration_postcode and general_profile.registration_postcode != "" and general_profile.registration_postcode != " ":
                postcode = general_profile.registration_postcode
            else:
                postcode = "00000"

            address = {
                  "flat_number": general_profile.registration_flat_nmb,
                  "building_number": general_profile.registration_building_nmb,
                  # "building_name": null,
                  "street": general_profile.registration_street,
                  # "sub_street": null,
                  "town": general_profile.registration_city,
                  "state": general_profile.registration_state,
                  "postcode": postcode,
                  "country": general_profile.registration_country_ISO_3_digits,
            }
            applicant_data["addresses"] = [address]
            json_data = json.dumps(applicant_data)

            custom_headers = {'Content-type': 'application/json', 'Authorization': token}
            r = requests.post(url, data=json_data, headers=custom_headers)
            print ("new applicant was created")
            result = r.json()
            print(result)
            applicant = IdentityVerificationApplicant.objects.create(general_profile=general_profile,
                                                         applicant_id=result["id"],
                                                         applicant_url=result["href"]
                                                         )

        #sending ID document scan
        #improve this later if it is needed to allow to send several files (for example scans of 2 pages of passport)
        last_doc = DocumentScan.objects.filter(general_profile=general_profile).last()
        url = "https://api.onfido.com/v2/applicants/%s/documents" % applicant.applicant_id
        f = last_doc.file.file
        file_name = last_doc.file.name.split("/")[-1]
        print(file_name)
        f.open(mode='rb')
        files = {'file': (file_name, f, 'image/jpeg')} #('file.py', open('file.py', 'rb'), 'text/plain')
        r = requests.post(url, files=files,  data={"type": last_doc.document_type},  headers=headers)
        f.close()#closing file after a call with it
        print( r.json())
        print ("ID scan was uploaded")

        #live photo uploading
        url = "https://api.onfido.com/v2/live_photos"
        f = general_profile.webcam_image.file
        file_name = last_doc.file.name.split("/")[-1]
        print(file_name)
        f.open(mode='rb')
        files = {'file': (file_name, f, 'image/jpeg')} #('file.py', open('file.py', 'rb'), 'text/plain')
        r = requests.post(url, files=files, data={
            "applicant_id": applicant.applicant_id,
            "advanced_validation": "false"
        }, headers=headers)
        f.close()#closing file after a call with it
        print( r.json())
        print ("live photo was uploaded")

        #creating check and saving check link
        url = "https://api.onfido.com/v2/applicants/%s/checks" % applicant.applicant_id
        r = requests.get(url, headers=headers)
        result = r.json()
        print ("all applicant's checks were retrieved")

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
                    print ("check was retrieved")
                    break

        if not previous_check_is_found:#create new check

            #Only identity report is available for sandbox (test_mode). For sandbox use the variant without other reports
            check_data = {
                "type": "express",
                "reports[][name]": ["identity"],
            }
            if ONFIDO_IS_TEST_MODE==False:
                check_data["reports[][name]"].append("document")

            r = requests.post(url, data=check_data, headers=headers)
            result = r.json()
            print(result)
            print ("check was created!!!")
            check = IdentityVerificationCheck.objects.create(applicant=applicant,
                                                             check_id=result["id"],
                                                             check_url=result["href"]
                                                             )


        #a call to get full info (not just ids) for the created reports
        url = "https://api.onfido.com/v2/checks/%s/reports" % check.check_id
        r = requests.get(url, headers=headers)
        print ("all reports in the ongoing check were retrieved")
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
            user.generalprofile.is_verified = True
            user.generalprofile.save(force_update=True)
        print ("Onfido API integration is finished")
        return HttpResponseRedirect(reverse("identity_verification_router"))
    else:
        return render(request, 'verifications/profile_identity_verification_photo.html', locals())


@csrf_exempt
@never_cache
def identity_verification_webhook(request):
    #Todo: add here infido ips to check + implement request token comparason
    data = json.loads(request.body.decode('utf-8'))
    data = data["payload"]
    report_href = data["object"]["href"]
    webhooklog = WebhookLog.objects.create(url=report_href)

    report_id = report_href.split("/")[-1]
    # print(report_id)
    #For testing purpose: replacing of onfido testing report id with some real report id from the testing database
    if report_id == "12345-23122-32123":
        report_id = "20a30bd1-03a7-4275-ab26-618e7850ffd9"

    try:
        report = IdentityVerificationReport.objects.get(report_id=report_id)
        token = "Token token=%s" % ONFIDO_TOKEN
        headers = {'Authorization': token}
        report_url = report.report_url
        r = requests.get(report_url, headers=headers)
        result = r.json()
        # print(result)
        report_result = result["result"]
        if report_result:
            report_result, created = VerificationReportResult.objects.get_or_create(name=report_result)

        report_status = result["status"]
        if report_status:
            report_status, created = VerificationReportStatus.objects.get_or_create(name=report_status)

        # print(report_status)
        # print(report_result)

        if report_status == 'complete' and report.type == 'document' and report_result != 'clear' or report_result != 'consider':
            general_profile = report.identification_checking.applicant.general_profile
            general_profile.is_verified = False
            general_profile.save(force_update=True)
        report.status = report_status
        report.result = report_result
        report.save(force_update=True)

        #to track if a webhook was processed successfully
        webhooklog.is_successfully_processed = True
        webhooklog.save(force_update=True)
    except Exception as e:
        # print(e)
        webhooklog.error_text = e
        webhooklog.save(force_update=True)

    return JsonResponse({})