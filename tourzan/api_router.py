"""
It is workaround solution to have all the urls in the one router
Reference is here: https://stackoverflow.com/questions/20825029/registering-api-in-apps
all urls are added to this router in each urls.py of each application
"""
from rest_framework import routers
class SharedAPIRootRouter(routers.SimpleRouter):

    #while urls are added to this class from each app.api.urls file, they are assigned to a class variable
    shared_router = routers.DefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        super().register(*args, **kwargs)