from django.conf.urls import url, include
from ..api import views
from tourzan.api_router import SharedAPIRootRouter


router = SharedAPIRootRouter()
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^push_notify/', views.push_notify_one),
]