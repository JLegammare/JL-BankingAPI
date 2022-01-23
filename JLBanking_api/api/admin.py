from django.contrib import admin

# Register your models here.

from django.contrib import admin
from api import models, constants
from django.contrib.auth.models import Group
from django.db.utils import OperationalError

# Registramos nuestro modelo
admin.site.register(models.Account)
admin.site.register(models.Transaction)

try:
    group, created = Group.objects.get_or_create(name=constants.GROUP_ADMIN)
    if created:
        print("Admin creado exitosamente")
    else:
        print("Admin ya existía, no fue creado")
    # Creamos el grupo de USER
    group, created = Group.objects.get_or_create(name=constants.GROUP_USER)
    if created:
        print("User creado exitosamente")
    else:
        print("User ya existía, no fue creado")
except OperationalError:
    print("No existe la base de datos de los grupos")
