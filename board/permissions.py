'''
from rest_framework import permissions

class CustomReadOnly(permissions.BasePermission):
# GET : 누구나 / PUT,PATCH : 해당 유저만

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: # 안전한 메소드(GET)면
            return True
        return obj.user == request.user
    '''

from rest_framework import permissions

class CustomReadOnly(permissions.BasePermission):
    """
    GET : 누구나 접근 가능
    POST, PATCH, DELETE : 작성자만 접근 가능
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS 요청은 모두 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 작성자와 요청 사용자가 일치해야 허용
        return obj.created_by == request.user