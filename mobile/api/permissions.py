# from rest_framework.permissions import BasePermission, SAFE_METHODS
#
#
# #the replacement of this permission is on re-applying of get_queryset method of API ViewSet in views
# class IsParticipant(BasePermission):
#
#     #object level permissions
#     def has_object_permission(self, request, view, obj):
#         user = request.user
#         if obj.guide == user or obj.tourist == user:
#             return True
#         else:
#             return False
#
#     #general level permissions
#     def has_permission(self, request, view):
#         return True
#
#
# #
# # class IsOwnerOrReadOnly(BasePermission):
# #     message = 'You must be the owner of this object.'
# #
# #     def has_object_permission(self, request, view, obj):
# #         if request.method in SAFE_METHODS:
# #             return True
# #         else:
# #             user = request.user
# #             if obj.guide == user or obj.tourist == user:
# #                 return True
# #             else:
# #                 return False