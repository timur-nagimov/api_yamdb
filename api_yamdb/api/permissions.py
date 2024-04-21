from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated and (request.user.is_staff
                                               or request.user.is_admin())
        )


class HasPrevilegesOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        is_safe_method = request.method in permissions.SAFE_METHODS
        is_auth = request.user.is_authenticated

        return is_safe_method or is_auth and (
            request.user.is_moder()
            or request.user.is_admin()
        )


class AllowGetOrIsAdminOrDeny(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            return request.user.is_authenticated and request.user.is_admin()


class IsAuthorOrHasAccess(permissions.BasePermission):

    def has_permission(self, request, view):
        is_safe_method = request.method in permissions.SAFE_METHODS
        return is_safe_method or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        is_safe_method = request.method in permissions.SAFE_METHODS
        is_auth = request.user.is_authenticated

        return is_safe_method or is_auth and (
            request.user.is_moder()
            or request.user.is_admin()
            or obj.author == request.user
        )


class IsAdminOrDeny(permissions.BasePermission):

    def has_permission(self, request, view):
        is_admin = request.user.is_authenticated and request.user.is_admin()

        return is_admin
