from django.conf.urls import url, include
from django.contrib import admin
from guides.api import views
from tourzan.api_router import SharedAPIRootRouter

"""
possible ways as well
"""
# guideprofile_detail = GuideProfileViewSet.as_view({
#     'get': 'retrieve',
#     'post': 'create',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
#
# guideprofile_list = GuideProfileViewSet.as_view({
#     'get': 'list',
#     'post': 'create',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy',
# })


# Create a router and register our viewsets with it.
#router automativally creates all the urls for ViewSet instance.
#if we you use GenericView instance like (ListCreateAPIView, RetrieveAPIView etc), they should be added to urls
#as 2 separte instances for actions with one object and with the list of objects like:
# url(r'^guideprofiles/$', guideprofile_list, name='guideprofile_list'),
# url(r'^guideprofiles/(?P<pk>[0-9]+)/$', guideprofile_detail, name='guideprofile_detail'),
#Refer to http://www.adamwester.me/blog/django-rest-framework-views/ for detailed explanation


router = SharedAPIRootRouter()
router.register(r'guides', views.GuideProfileViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'guide_services', views.GuideServiceViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),

    # url(r'^guideprofiles/$', guideprofile_list, name='guideprofile_list'),
    # url(r'^guideprofiles/(?P<pk>[0-9]+)/$', guideprofile_detail, name='guideprofile_detail'),

    # url(r'^create/$', GuideProfileCreateAPIView.as_view(), name='create'),
    # url(r'^(?P<slug>[\w-]+)/$', GuideProfileDetailAPIView.as_view(), name='detail'),
    # url(r'^(?P<slug>[\w-]+)/edit/$', GuideProfileUpdateAPIView.as_view(), name='update'),
    # url(r'^(?P<slug>[\w-]+)/delete/$', GuideProfileDeleteAPIView.as_view(), name='delete'),
]