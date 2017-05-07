from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),

    url(r'^general_settings/$', views.general_settings, name='general_settings'),


    url(r'^set_language/(?P<language>\w+)/$', views.set_language, name='set_language'),
    url(r'^change_role/$', views.change_role, name='change_role'),

    url(r'^change_role/(?P<new_role>\w+)/$', views.change_role, name='change_role_settings'),

    url(r'^settings/$', views.settings_router, name='settings_router'),

    url(r'^search_interest/$', views.search_interest, name='search_interest'),

]
