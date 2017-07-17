"""tourzan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from users.api.views import login_api_view, signup_api_view

from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework.schemas import get_schema_view
from .api_router import SharedAPIRootRouter


schema_view = get_schema_view(title='Pastebin API')


#returning of all the SharedAPIRootRouter urls (which are added there in each app.api.url file)
#before returning of them they are being imported dynamically here
def api_urls():
    return SharedAPIRootRouter.shared_router.urls


#added here i18n_patterns for localization
urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^', include('chats.urls')),
    url(r'^', include('locations.urls')),
    url(r'^', include('orders.urls')),
    url(r'^', include('tours.urls')),
    url(r'^', include('users.urls')),

    url(r'^', include('guides.urls')),
    url(r'^', include('tourists.urls')),
    url(r'^', include('payments.urls')),

    url(r'^', include('website_management.urls')),
    url(r'^', include('blog.urls')),


    url(r'^accounts/', include('allauth.urls')),
    url(r'^summernote/', include('django_summernote.urls')),


    #for mobiles
    #to access protected api urls you must include the Authorization: JWT <your_token> header.
    #https://getblimp.github.io/django-rest-framework-jwt/
    #http://polyglot.ninja/django-rest-framework-json-web-tokens-jwt/
    url(r'^api/v1/api-token-auth/', obtain_jwt_token),
    url(r'^api/v1/api-token-verify/', verify_jwt_token),

    url(r'^api/v1/login_client/$', login_api_view, name='login_client'),
    url(r'^api/v1/signup_client/$', signup_api_view, name='signup_client'),


    url(r'^api/v1/', include('chats.api.urls')),
    url(r'^api/v1/', include('tourists.api.urls')),
    url(r'^api/v1/', include('guides.api.urls')),
    url(r'^api/v1/', include('tours.api.urls')),
    url(r'^api/v1/', include('orders.api.urls')),
    url(r'^api/v1/', include('locations.api.urls')),
    url(r'^api/v1/', include('users.api.urls')),
    url(r'^api/v1/', include('blog.api.urls')),

    url(r'^api/v1/', include(api_urls())),#for the main representation page of Django Rest Framework


    url(r'^api/v1/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/schema/$', schema_view),

)\
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
