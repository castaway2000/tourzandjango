from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )
from .permissions import IsUserOwnerOrReadOnly

from allauth.account.views import password_reset
from django.core import serializers as serial
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpRequest
from django.core.files import File

from rest_framework.decorators import api_view, authentication_classes, permission_classes, list_route
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

import urllib3
import json
import ast
from PIL import Image
from base64 import decodebytes
import tempfile

from rest_framework import viewsets
from ..models import *
from orders.models import Review, Order
from mobile.models import GeoTracker
from user_verification.models import IdentityVerificationApplicant, IdentityVerificationReport, IdentityVerificationCheck
from users.models import UserInterest
from .serializers import *
from .permissions import IsUserOwnerOrReadOnly

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from utils.api_helpers import FilterViewSet
from utils.internalization_wrapper import languages_english


class InterestViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class UserInterestViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = UserInterest.objects.all()
    serializer_class = UserInterestSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)


class LanguageLevelViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = LanguageLevel.objects.all()
    serializer_class = LanguageLevelSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class UserLanguageViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = UserLanguage.objects.all()
    serializer_class = UserLanguageSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)


##Reference http://polyglot.ninja/django-rest-framework-authentication-permissions/
##use this for clients token creation
@api_view(["POST"])
def login_api_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "Login failed"}, status=HTTP_401_UNAUTHORIZED)

    if not hasattr(user, 'partner'):
        return Response({"error": "This user not signed up as a partner with API access"}, status=HTTP_401_UNAUTHORIZED)

    if not user.partner.is_active:
        return Response({"error": "API access partner status is not active"}, status=HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


#Sign up for API tokens is done in other workflow
@api_view(["POST"])
def signup_api_view(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password1 = request.data.get("password1")
    password2 = request.data.get("password2")
    if User.objects.filter(username=username).exists():
        return Response({"error": "Signup failed: such username exists"}, status=HTTP_401_UNAUTHORIZED)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Signup failed: such email already exists"}, status=HTTP_401_UNAUTHORIZED)

    if password1 != password2:
        return Response({"error": "Signup failed: passwords do not match"}, status=HTTP_401_UNAUTHORIZED)

    user = User.objects.create_user(username=username, email=email, password=password1)
    if not user:
        return Response({"error": "Signup failed during creation a new user"}, status=HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


def try_or_none(orm):
    try:
        data = orm
    except Exception:
        data = None
    return data


@api_view(['POST'])
def get_jwt_user(request):
    print("get jwt")
    username = request.data.get("username")
    password = request.data.get("password")
    user_auth = authenticate(username=username, password=password)
    print(user_auth)
    if not user_auth:
        return Response({"error": "Login failed"}, status=HTTP_401_UNAUTHORIZED)
    user = User.objects.get(username=username)
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    user_obj = {'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name':  user.last_name,
                'email': user.email,
                'phone': user.generalprofile.phone,
                'building_num': user.generalprofile.registration_building_nmb,
                'flat_num': user.generalprofile.registration_flat_nmb,
                'street': user.generalprofile.registration_street,
                'city': user.generalprofile.registration_city,
                'state': user.generalprofile.registration_state,
                'country': user.generalprofile.registration_country,
                'postcode': user.generalprofile.registration_postcode,
                'interests': [],
                'guide_id': None,
                'profile_picture': None,
                }
    for i in user.userinterest_set.all():
        user_obj['interests'].append(i.interest.name)
    if hasattr(user, 'guideprofile'):
        user_obj['guide_id'] = user.guideprofile.id
    try:
        user_obj['profile_picture'] = str(user.touristprofile.image.url)
    except Exception as err:
        print(err)
        pass

    token_user = {"token": token, 'user': user_obj}
    return Response(token_user)


@api_view(['post'])
def api_change_pass(request):
    if request.method == 'POST':
        tokenize = json.dumps({'token': request.POST['token']})
        http = urllib3.PoolManager()
        req = http.request('POST',  '{}/validate_token'.format(request.get_host()),
                           headers={'Content-Type': 'application/json'},
                           body=tokenize)
        if req.status != 200:
            return HTTP_401_UNAUTHORIZED('please login')
        user = request.user
        form = PasswordChangeForm(data=request.POST or None, user=user)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            update_session_auth_hash(request, user)
            return HttpResponse(status=HTTP_200_OK)


@api_view(['POST'])
def forgot_password(request):
    if request.method == 'POST':
        email = json.dumps({'email': request.POST['email']})
        http = urllib3.PoolManager()
        #TODO: update the url
        req = http.request('POST',  '{}/reset_password'.format(request.get_host()),
                           headers={'Content-Type': 'application/json'},
                           body=email)
        return HttpResponse(status=req.status)


@api_view(['POST'])
def user_profile(request):
    if request.method == 'POST':
        try:
            if request.POST['user_id']:
                print(request.POST)
                user_id = request.POST['user_id']
                user = User.objects.get(id=user_id)

                def get_tourist_representation_by_id(user):
                    tourist = TouristProfile.objects.get(user=user)
                    qs = Review.objects.filter(order__tourist=tourist, is_guide_feedback=True).order_by('-id')
                    data = json.loads(serial.serialize('json', qs))
                    for d in data:
                        order = Order.objects.get(id=d['fields']['order'])
                        d['fields']['reviewers_picture'] = None
                        d['fields']['reviewers_name'] = order.guide.name
                        try:
                            d['fields']['reviewers_picture'] = str(order.guide.profile_image.url)
                        except Exception as err:
                            print(err)
                            pass
                    return data

                def get_guide_representation_by_id(user):
                    gp = GuideProfile.objects.get(user=user)
                    qs = Review.objects.filter(order__guide=gp, is_tourist_feedback=True).order_by('-id')
                    data = json.loads(serial.serialize('json', qs))
                    for d in data:
                        order = Order.objects.get(id=d['fields']['order'])
                        d['fields']['reviewers_picture'] = None
                        d['fields']['reviewers_name'] = order.tourist.user.generalprofile.first_name
                        try:
                            d['fields']['reviewers_picture'] = str(order.tourist.image.url)
                        except Exception as err:
                            print(err)
                            pass
                    return data

                def if_guide():
                    data = {'is_guide': False, 'is_default': False, 'profile_image': None, 'guide_overview': None,
                            'guide_rating': 0, 'reviews': None}
                    if hasattr(user, 'guideprofile'):
                        data['reviews'] = get_guide_representation_by_id(user)
                        data['is_guide'] = True
                        data['is_default'] = user.guideprofile.is_default_guide
                        data['guide_overview'] = user.guideprofile.overview
                        data['guide_rating'] = user.guideprofile.rating
                        data['first_name'] = user.first_name
                        data['last_name'] = user.last_name
                        try:
                            data['profile_image'] = str(user.guideprofile.profile_image.url)
                        except Exception as e:
                            print(e)
                            data['profile_image'] = None
                    return data
                try:
                    geotracker = GeoTracker.objects.get(user_id=user.id)
                    lat = geotracker.latitude
                    lon = geotracker.longitude
                except Exception as err:
                    print(err)
                    lat = None
                    lon = None

                try:
                    idva = IdentityVerificationApplicant.objects.get(general_profile_id=user.id)
                    idvr = IdentityVerificationReport.objects.filter(identification_checking__applicant__applicant_id=idva.applicant_id,
                                                                     type=1).last()
                    verification_status = str(idvr.status)
                    verification_result = str(idvr.result)
                except Exception as err:
                    print(err)
                    verification_status = None
                    verification_result = None
                res = { 'id': user_id,
                        'profile_picture': None,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'about_tourist': user.touristprofile.about,
                        'tourist_rating': user.touristprofile.rating,
                        'is_fee_free': user.generalprofile.is_fee_free,
                        'is_trusted': user.generalprofile.is_trusted,
                        'is_verified': user.generalprofile.is_verified,
                        'verification_result': verification_result,
                        'verification_status': verification_status,
                        'referral_code': user.generalprofile.referral_code,
                        'latitude': lat,
                        'longitude': lon,
                        'interests': [],
                        'tourist_reviews': get_tourist_representation_by_id(user),
                        'guide_data': if_guide()
                        }
                for i in user.userinterest_set.all():
                    res['interests'].append(i.interest.name)
                try:
                    res['profile_picture'] = str(user.touristprofile.image.url)
                except Exception as error:
                    print(error)
                    pass
                return Response(res)
        except Exception as err:
            print('ERROR: ', err)
            return HttpResponse(json.dumps({'status': 400, 'detail': str(err)}))


class EditProfileViewSet(viewsets.ModelViewSet):
    queryset = GeneralProfile.objects.all()
    serializer_class = GeneralProfileSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)
    http_method_names = ('get',)

    def get_tourist_representation_by_id(self, user):
        qs = Review.objects.filter(order__tourist__user=user, is_tourist_feedback=True).order_by('-id')
        data = json.loads(serial.serialize('json', qs))
        for d in data:
            order = Order.objects.get(id=d['fields']['order'])
            d['fields']['reviewers_picture'] = str(order.guide.profile_image.url)
            d['fields']['reviewers_name'] = order.guide.name
        return data

    # def if_guide(self, user):
    #     data = {'is_guide': False, 'is_default': False, 'profile_image': None, 'guide_overview': None,
    #             'guide_rating': 0, 'reviews': None}
    #     if hasattr(user, 'guideprofile'):
    #         data['reviews'] = self.get_guide_representation_by_id(user)
    #         data['is_guide'] = True
    #         data['is_default'] = user.guideprofile.is_default_guide
    #         data['guide_overview'] = user.guideprofile.overview
    #         data['guide_rating'] = user.guideprofile.rating
    #         try:
    #             data['profile_image'] = str(user.guideprofile.profile_image.url)
    #         except Exception as e:
    #             print(e)
    #     return data

    @list_route()
    def edit_profile(self, request):
        try:
            user = request.user
            get = request.GET
            print(get)
            if user:
                gp = GeneralProfile.objects.get(id=user.generalprofile.id)
                tp = TouristProfile.objects.get(id=user.touristprofile.id)
                uo = User.objects.get(id=user.id)
                try:
                    idva = IdentityVerificationApplicant.objects.get(general_profile_id=user.id)
                    idvr = IdentityVerificationReport.objects.filter(
                        identification_checking__applicant__applicant_id=idva.applicant_id,
                        type=1).last()
                    verification_status = str(idvr.status)
                    verification_result = str(idvr.result)
                except Exception as err:
                    print(err)
                    verification_status = None
                    verification_result = None
                try:
                    geotracker = GeoTracker.objects.get(user_id=user.id)
                    lat = geotracker.latitude
                    lon = geotracker.longitude
                except Exception as err:
                    print(err)
                    lat = None
                    lon = None

                # if 'first_name' in get.keys:
                gp.first_name = get['first_name']
                # if get['last_name']:
                gp.last_name = get['last_name']
                # if get['about']:
                tp.about = get['about']
                # if get['profession']:
                gp.profession = get['profession']
                if get['dob'] != '0' and get['dob'] is not None and get['dob'] != 'null':
                    date_of_birth = datetime.datetime.strptime(get['dob'], '%m/%d/%Y')
                    gp.date_of_birth = date_of_birth
                else:
                    gp.date_of_birth = None
                uo.save(force_update=True)
                gp.save(force_update=True)
                tp.save(force_update=True)

                interests = ast.literal_eval(get['interests'])
                active_interests = None
                if interests:
                    gp.set_interests_from_list(interests)
                    user_interests = UserInterest.objects.filter(user=user, is_active=True)
                    active_interests = []
                    for u in user_interests:
                        active_interests.append(str(u.interest))

                languages = get['languages'] #requires format [ {"name": "english", "level": language_level_id} ]
                if languages:
                    user_language = ast.literal_eval(languages)
                    active_languages = [ast.literal_eval(languages)]
                    for i in user_language:
                        for l in languages_english:
                            if i['name'] == l[1]:
                                i['name'] = l[0]
                                break
                    gp.set_languages_from_list(user_language)
                # for idx, language in enumerate(gp.get_languages()):
                #     if language is not None:
                #         active_languages.append({'name': str(language), 'level': idx+1})

                res = {'id': user.generalprofile.id,
                        'profile_picture': None,
                        'username': user.username,
                        'first_name': user.generalprofile.first_name,
                        'last_name': user.generalprofile.last_name,
                        'about_tourist': user.touristprofile.about,
                        'tourist_rating': user.touristprofile.rating,
                        'is_fee_free': user.generalprofile.is_fee_free,
                        'is_trusted': user.generalprofile.is_trusted,
                        'is_verified': user.generalprofile.is_verified,
                        'verification_result': verification_result,
                        'verification_status': verification_status,
                        'referral_code': user.generalprofile.referral_code,
                        'latitude': lat,
                        'longitude': lon,
                        'interests': active_interests,
                        'languages': active_languages,
                        'tourist_reviews': self.get_tourist_representation_by_id(user),
                        }
                return Response(res)
            else:
                return Response({'detail': 'bad credentials'})
        except Exception as err:
            raise err
            return Response({'error': 400, 'detail': str(err)})

    @list_route()
    def edit_guide_profile(self, request):
        try:
            user = request.user
            get = request.GET
            if user:
                uo = User.objects.get(id=user.id)
                gp = GeneralProfile.objects.get(id=user.generalprofile.id)
                city = City.objects.get_or_create(name=get['city'])[0]
                if hasattr(uo, 'guideprofile'):
                    gup = GuideProfile.objects.get(user=uo)
                else:
                    gup = GuideProfile.objects.create(user=uo, city=city)
                try:
                    idva = IdentityVerificationApplicant.objects.get(general_profile_id=user.id)
                    idvr = IdentityVerificationReport.objects.filter(
                        identification_checking__applicant__applicant_id=idva.applicant_id, type=1).last()
                    verification_status = str(idvr.status)
                    verification_result = str(idvr.result)
                except Exception as err:
                    print(err)
                    verification_status = None
                    verification_result = None
                try:
                    geotracker = GeoTracker.objects.get_or_create(user_id=user.id)
                    lat = geotracker.latitude
                    lon = geotracker.longitude
                except Exception as err:
                    print(err)
                    lat = None
                    lon = None
                if get['dob'] != '0' and get['dob'] is not None and get['dob'] != 'null':
                    date_of_birth = datetime.datetime.strptime(get['dob'], '%m/%d/%Y')
                    gup.date_of_birth = date_of_birth
                else:
                    gup.date_of_birth = None

                gp.first_name = get['first_name']
                gp.last_name = get['last_name']
                gup.name = get['first_name']
                gup.rate = get['rate']
                gup.overview = get['overview']
                gup.city = city
                uo.save(force_update=True)
                gp.save(force_update=True)
                gup.save(force_update=True)
                interests = ast.literal_eval(get['interests'])
                active_interests = None
                if interests:
                    gp.set_interests_from_list(interests)
                    user_interests = UserInterest.objects.filter(user=user, is_active=True)
                    active_interests = []
                    for u in user_interests:
                        active_interests.append(str(u.interest))

                languages = get['languages'] #requires format [ {"name": "english", "level": language_level_id} ]
                if languages:
                    user_language = ast.literal_eval(languages)
                    active_languages = [ast.literal_eval(languages)]
                    for i in user_language:
                        for l in languages_english:
                            if i['name'] == l[1]:
                                i['name'] = l[0]
                                break
                    gp.set_languages_from_list(user_language)
                # active_languages = []
                # for idx, language in enumerate(gp.get_languages()):
                #     if language is not None:
                #         active_languages.append({'name': str(language), 'level': idx+1})

                res = {'id': user.generalprofile.id,
                       'profile_picture': None,
                       'username': user.username,
                       'first_name': gp.first_name,
                       'last_name': gp.last_name,
                       'overview': gup.overview,
                       'guide_rating': gup.rating,
                       'is_active': gup.is_active,
                       'is_fee_free': gp.is_fee_free,
                       'is_trusted': gp.is_trusted,
                       'is_verified': gp.is_verified,
                       'verification_result': verification_result,
                       'verification_status': verification_status,
                       'referral_code': gp.referral_code,
                       'latitude': lat,
                       'longitude': lon,
                       'city': gup.city.name,
                       'interests': active_interests,
                       'languages': active_languages,
                       'tourist_reviews': self.get_tourist_representation_by_id(user),
                       }
                return Response(res)
            else:
                return Response({'detail': 'bad credentials or not a guide'})
        except Exception as err:
            return Response({'error': 400, 'detail': str(err)})


@api_view(['POST'])
def upload_profile_image(request):
    try:
        user = request.user
        data = request.POST
        user_type = data['user_type']
        signature_data = bytes(data['image'], 'UTF-8')
        signature_data = decodebytes(signature_data)
        with tempfile.NamedTemporaryFile(mode='w+b', delete=True) as jpg:
            jpg.write(signature_data)
            Image.open(jpg).verify()  # test image before the image is saved
            if user_type == 'tourist':
                tourist = TouristProfile.objects.get(id=user.touristprofile.id)
                tourist.image = File(jpg)
                tourist.save(force_update=True)
            elif user_type == 'guide':
                guide = GuideProfile.objects.get(id=user.guideprofile.id)
                guide.profile_image = File(jpg)
                guide.save(force_update=True)
        return HttpResponse(json.dumps({'detail': 'success', 'status': 200}))
    except Exception as err:
        return HttpResponse(json.dumps({'detail': err, 'status': 400}))


@api_view(['POST'])
def user_mixins(request):
    try:
        id = int(request.POST['id'])
        user_type = request.POST['user_type']
        data = GeneralProfile.objects.get(user=id)
        username = data.user.username
        firstname = data.first_name
        lastname = data.last_name
        if user_type == 'guide':
            try:
                pic = data.user.guideprofile.profile_image.url
            except Exception as err:
                print(err)
                pic = None
        else:
            pic = data.user.touristprofile
            if hasattr(pic, 'image'):
                try:
                    pic = pic.image.url
                except ValueError as err:
                    print(err)
                    pic = None
            else:
                pic = None
        return HttpResponse(json.dumps({'id': id, 'username': username, 'first_name': firstname,
                                        'last_name': lastname, 'pic': pic}))
    except Exception as err:
        print(err)
        return HttpResponse(json.dumps({'status': 400, 'detail': str(err)}))


@api_view(['POST'])
def get_my_profile_info(request):
    try:
        user = request.user
        gp = GeneralProfile.objects.get(user=user)
        tp = dict()
        gpd = dict()
        genp = dict()
        tourist_profile = model_to_dict(gp.user.touristprofile)
        for k, v in tourist_profile.items():
            if k == 'image':
                try:
                    tp[k] = gp.user.touristprofile.image.url
                    if hasattr(v, 'url'):
                        tp[k] = str(v.url) if v.url else ''
                except:
                    tp[k] = None
            else:
                tp[k] = v
        general_profile = model_to_dict(gp)
        for k, v in general_profile.items():
            if 'image' in k:
                try:
                    genp[k] = str(v.url)
                except:
                    genp[k] = None
            else:
                genp[k] = v
        genp['interests'] = []
        genp['languages'] = {}
        try:
            geotracker = GeoTracker.objects.get(user_id=user.id)
            lat = geotracker.latitude
            lon = geotracker.longitude
        except Exception as err:
            print(err)
            lat = None
            lon = None

        try:
            idva = IdentityVerificationApplicant.objects.get(general_profile_id=user.id)
            idvr = IdentityVerificationReport.objects.filter(
                identification_checking__applicant__applicant_id=idva.applicant_id,
                type=1).last()
            verification_status = str(idvr.status)
            verification_result = str(idvr.result)
        except Exception as err:
            print(err)
            verification_status = None
            verification_result = None
        genp['latitude'] = lat
        genp['longitude'] = lon
        gpd['verification_status'] = verification_status
        gpd['verification_result'] = verification_result

        if hasattr(gp.user, 'guideprofile'):
            guide_profile = model_to_dict(gp.user.guideprofile)
            try:
                guide_profile['city_id'] = gp.user.guideprofile.city.id
                guide_profile['city'] = gp.user.guideprofile.city.name
            except Exception:
                guide_profile['city_id'] = None
                guide_profile['city'] = None

            for k, v in guide_profile.items():
                if 'image' in k:
                    try:
                        gpd[k] = str(v.url)
                    except:
                        gpd[k] = None
                else:
                    gpd[k] = v
        for i in user.userinterest_set.all():
            genp['interests'].append(i.interest.name)

        user_languages = UserLanguage.objects.filter(user=user, is_active=True).all()
        for i in user_languages:
            for l in languages_english:
                if i.language == l[0]:
                    lang = l[1]
                    break
            else:
                lang = i.language
            genp['languages'][str(i.level.name)] = lang
            genp['languages']['{}_language_id'.format(i.level.name)] = i.id

        data = {'tourist_profile': tp, 'guide_profile': gpd, 'general_profile': genp}
        return Response(data)
    except Exception as err:
        return Response({'status': 400, 'detail': str(err)})
