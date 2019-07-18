# Create a router and register our viewsets with it.
#router automativally creates all the urls for ViewSet instance.
#if we you use GenericView instance like (ListCreateAPIView, RetrieveAPIView etc), they should be added to urls
#as 2 separte instances for actions with one object and with the list of objects like:
# url(r'^guideprofiles/$', guideprofile_list, name='guideprofile_list'),
# url(r'^guideprofiles/(?P<pk>[0-9]+)/$', guideprofile_detail, name='guideprofile_detail'),
#Refer to http://www.adamwester.me/blog/django-rest-framework-views/ for detailed explanation

from django.conf.urls import url, include
from ..api import views
from tourzan.api_router import SharedAPIRootRouter


router = SharedAPIRootRouter()
router.register(r'interests', views.InterestViewSet)
router.register(r'user_interests', views.UserInterestViewSet)
router.register(r'language_levels', views.LanguageLevelViewSet)
router.register(r'user_languages', views.UserLanguageViewSet)
router.register(r'edit_profile', views.EditProfileViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^user_profile/', views.user_profile, name='user_profile'),
    url(r'^user_mixins/', views.user_mixins, name='user_mixins'),
    url(r'^get_my_profile_info/', views.get_my_profile_info, name='get_my_profile_info'),
    url(r'^upload_profile_image/', views.upload_profile_image, name='upload_profile_image')
]