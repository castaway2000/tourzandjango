from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^privacy-policy/$', views.privacy_policy, name='privacy_policy'),
    url(r'^about-us/$', views.about_us, name='about_us'),
    url(r'^tos/$', views.tos, name='tos'),
    url(r'^integration-terms/$', views.integration_contract, name='integration_terms'),
    url(r'^contact-us/$', views.contact_us, name='contact_us'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^press/$', views.press, name='press'),
    url(r'^developer-documentation/$', views.developer_documentation, name='developer_documentation')

]
