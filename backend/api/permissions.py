from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrReadOnly(BasePermission):
    """
    Изменять и добавлять объекты может
    только их автор или администратор.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)
