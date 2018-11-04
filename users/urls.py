from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),

    url(r'^after_login_router/$', views.after_login_router, name='after_login_router'),

    url(r'^general_settings/$', views.general_settings, name='general_settings'),
    url(r'promotions/$', views.promotions, name='promotions'),

    url(r'^set_language/(?P<language>\w+)/$', views.set_language, name='set_language'),
    url(r'^change_role/$', views.change_role, name='change_role'),

    url(r'^change_role/(?P<new_role>\w+)/$', views.change_role, name='change_role_settings'),

    url(r'^settings/$', views.settings_router, name='settings_router'),

    url(r'^search_interest/$', views.search_interest, name='search_interest'),
    url(r'^search_language/$', views.search_language, name='search_language'),
    url(r'^accounts/signup/$', views.SignupViewCustom.as_view(), name='account_signup'),
    url(r'^password_changing/$', views.password_changing, name='password_changing'),

    url(r'^sending_sms_code/$', views.sending_sms_code, name='sending_sms_code'),
    url(r'^authorization-options/$', views.authorization_options, name='authorization_options'),
    url(r'^express-signup-completing/(?P<uuid>\w+)/$', views.express_signup_completing, name='express_signup_completing'),
]
