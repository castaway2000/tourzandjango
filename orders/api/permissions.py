from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTouristOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.tourist.user == request.user


class IsTouristOrGuideOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        try:
            user = request.user
            print(user)
            if obj.order.guide.user == user or obj.order.tourist.user == user:
                return True
            else:
                return False
        except:
            return False
