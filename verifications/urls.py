from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^identity_verification/$', views.identity_verification_router, name='identity_verification_router'),
    url(r'^identity_verification/ID_uploading/$', views.identity_verification_ID_uploading, name='identity_verification_ID_uploading'),
    url(r'^identity_verification/photo/$', views.identity_verification_photo, name='identity_verification_photo'),
    url(r'^identity_verification/onfidowebhook/$', views.identity_verification_webhook, name='identity_verification_webhook'),
]