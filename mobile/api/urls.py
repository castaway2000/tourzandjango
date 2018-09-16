from django.conf.urls import url, include
from mobile.api import views
from tourzan.api_router import SharedAPIRootRouter

router = SharedAPIRootRouter()
urlpatterns = [url(r'^', include(router.urls)),
               url(r'^get_nearby_guides/', views.show_nearby_guides),
               url(r'^get_trip_status/', views.get_trip_status),
               url(r'^update_trip/', views.update_trip),
               url(r'^extend_time/', views.extend_time),
               url(r'^book_guide/', views.book_guide),
               url(r'^review/', views.create_review),
               ]