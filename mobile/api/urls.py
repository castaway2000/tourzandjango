from django.conf.urls import url, include
from mobile.api import views
from tourzan.api_router import SharedAPIRootRouter

router = SharedAPIRootRouter()
router.register(r'create_trip', views.create_trip)
router.register(r'get_trip', views.get_trip)
router.register(r'update_trip', views.update_trip)
router.register(r'end_trip', views.end_trip)

urlpatterns = [url(r'^', include(router.urls))]
