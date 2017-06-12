from django.conf.urls import url, include
from ..api import views
from rest_framework.routers import DefaultRouter
from tourzan.api_router import SharedAPIRootRouter

# Create a router and register our viewsets with it.
#router automativally creates all the urls for ViewSet instance.
#if we you use GenericView instance like (ListCreateAPIView, RetrieveAPIView etc), they should be added to urls
#as 2 separte instances for actions with one object and with the list of objects like:
# url(r'^guideprofiles/$', guideprofile_list, name='guideprofile_list'),
# url(r'^guideprofiles/(?P<pk>[0-9]+)/$', guideprofile_detail, name='guideprofile_detail'),
#Refer to http://www.adamwester.me/blog/django-rest-framework-views/ for detailed explanation


router = SharedAPIRootRouter()
router.register(r'chats', views.ChatViewSet)
router.register(r'chat_messages', views.ChatMessageViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]