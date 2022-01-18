from django.contrib import admin

# Register your models here.

from django.contrib import admin
# Importamos nuestros modelos
from api import models
# Registramos nuestro modelo
admin.site.register(models.Account)