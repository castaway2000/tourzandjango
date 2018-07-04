from django.conf.urls import url, include
from mobile.api import views
from tourzan.api_router import SharedAPIRootRouter

router = SharedAPIRootRouter()
# router.register(r'get_trip_status', views.get_trip_status)
# router.register(r'update_trip', views.update_trip)
# router.register(r'extend_time', views.extend_time)
# router.register(r'book_guide', views.book_guide)


urlpatterns = [url(r'^', include(router.urls)),
               url(r'^get_trip_status/', views.get_trip_status),
               url(r'^update_trip/', views.update_trip),
               url(r'^extend_time/', views.extend_time),
               url(r'^book_guide/', views.book_guide)
               ]
