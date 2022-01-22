from api import constants, models
from rest_framework.permissions import BasePermission


# La clase IsAdmin es nuestro permiso, que tiene que extender de BasePermission para que sea un permiso
class IsAdmin(BasePermission):
    message = "El usuario no es admin"

    def has_permission(self, request, view):
        if not request.user.groups.exists():
            return False
        # Asumimos en este caso que cada usuario va a tener 1 solo grupo, aunque puede tener más
        # Este código funciona solo si tiene 1 grupo
        return request.user.groups.all()[0].name == constants.GROUP_ADMIN


class IsUser(BasePermission):
    message = "El usuario no es user"

    def has_permission(self, request, view):
        if not request.user.groups.exists():
            return False
        return request.user.groups.all()[0].name == constants.GROUP_USER

