from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGuideOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        print("has obj permissions")
        if request.method in SAFE_METHODS:
            return True
        return obj.guide.user == request.user


class IsTourGuideOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        print("has obj permissions")
        if request.method in SAFE_METHODS:
            return True
        return obj.tour.guide.user == request.user