from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django.http.response import HttpResponse

from ..models import *
from .serializers import *
from .permissions import IsParticipant
from django.db.models import Q
from utils.api_helpers import FilterViewSet

import json



class ChatViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'create']

    def get_queryset(self):
        user = self.request.user
        qs = Chat.objects.filter(Q(guide=user)|Q(tourist=user))
        return qs

    @list_route()
    def get_guide_representation(self, request):
        user = request.user
        qs = Chat.objects.filter(guide=user).order_by('-id')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def get_tourist_representation(self, request):
        user = request.user
        qs = Chat.objects.filter(tourist=user).order_by('-id')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ChatMessageViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'create']

    def get_queryset(self):
        user = self.request.user
        qs = ChatMessage.objects.filter(Q(chat__guide=user)|Q(chat__tourist=user))
        return qs

    @list_route()
    def get_guide_representation(self, request):
        user = request.user
        qs = ChatMessage.objects.filter(chat__guide=user).order_by('-id')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def get_tourist_representation(self, request):
        user = request.user
        qs = ChatMessage.objects.filter(chat__tourist=user).order_by('-id')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def send_message(self, request):
        try:
            user = request.user
            chat_id = request.GET['chat_id']
            chat_uuid = request.GET['chat_uuid'] # needs both uuid and id to prevent id targeting
            msg = request.GET['message']
            chat = Chat.objects.get(id=chat_id, uuid=chat_uuid)
            if user.id == chat.tourist.id or user.id == chat.guide.id:
                chat.create_message(user=user, message=msg)
            return HttpResponse(json.dumps({'message': msg}))
        except Exception:
            return HttpResponse(json.dumps({'errors': [{'status': 403}]}))