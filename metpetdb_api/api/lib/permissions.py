from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow:
        - owners of an object to edit it
        - owners of a private object to view it
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        has_perm = False
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            has_perm = (obj.public_data == True)

        # Write permissions are only allowed to the owner of the snippet.
        if request.user.is_active and obj.owner == request.user:
            has_perm = True

        return has_perm


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow:
        - superusers to edit an object
        - everyone else to view it
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        has_perm = False
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            has_perm = True

        return has_perm


class UserPermission(permissions.BasePermission):
    """
    Custom permission to only allow:
        - superusers to edit a user
        - users to view their own details
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        has_perm = False

        # Users are allowed to view their own details
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_active and obj == request.user:
                has_perm = True

        return has_perm
