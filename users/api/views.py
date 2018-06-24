from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from allauth.account.views import password_reset
from django.contrib.auth import authenticate
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
import urllib3
import json

from rest_framework import viewsets
from ..models import *
from orders.models import Review, Order
from .serializers import *
from .permissions import IsUserOwnerOrReadOnly

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


class InterestViewSet(viewsets.ModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class UserInterestViewSet(viewsets.ModelViewSet):
    queryset = UserInterest.objects.all()
    serializer_class = UserInterestSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)


class LanguageLevelViewSet(viewsets.ModelViewSet):
    queryset = LanguageLevel.objects.all()
    serializer_class = LanguageLevelSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class UserLanguageViewSet(viewsets.ModelViewSet):
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

                def if_guide():
                    data = {'is_guide': False, 'is_default': False, 'profile_image': None, 'guide_overview': None,
                            'guide_rating': 0}
                    if hasattr(user, 'guideprofile'):
                        data['is_guide'] = True
                        data['is_default'] = user.guideprofile.is_default_guide
                        data['guide_overview'] = user.guideprofile.overview
                        data['guide_rating'] = user.guideprofile.rating
                        try:
                            data['profile_image'] = str(user.guideprofile.profile_image.url)
                        except Exception as e:
                            print(e)
                    return data

                res = { 'id': user_id,
                        'profile_picture': None,
                        'first_name': user.generalprofile.first_name,
                        'last_name': user.generalprofile.last_name,
                        'about_tourist': user.touristprofile.about,
                        'tourist_rating': user.touristprofile.rating,
                        'interests': [],
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
            return HttpResponse(status=HTTP_400_BAD_REQUEST)


