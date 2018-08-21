from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import live_chat.routing
from live_chat.utils import TokenAuthMiddlewareStack

import mobile.routing


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            live_chat.routing.websocket_urlpatterns,
        )
    ),
})