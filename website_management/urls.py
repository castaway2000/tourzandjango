from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^privacy_policy/$', views.privacy_policy, name='privacy_policy'),
    url(r'^about_us/$', views.about_us, name='about_us'),
    url(r'^tos/$', views.tos, name='tos'),
    url(r'^integration_terms/$', views.integration_contract, name='integration_terms'),
    url(r'^contact_us/$', views.contact_us, name='contact_us'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^sitemap/$', views.sitemap, name='sitemap'),

]
