from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException
from rest_framework import status


class GenericAPIException(APIException):
    def __init__(self, status_code, detail=None, code=None):
        self.status_code = status_code
        super().__init__(detail=detail, code=code)


class IsOwner(BasePermission):
    """
    사용자가 자신 가계부에만 접근 가능
    다른 사용자는 접근 불가
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.owner == user:
            return True
        
        if user.is_authenticated or user.is_anonymous:
            response = {"detail":"접근 권한 없습니다."}
            raise GenericAPIException(status_code=status.HTTP_403_FORBIDDEN, detail=response)