from django.db import models

# Create your models here.

# Importamos el modelo User default de Django
from django.contrib.auth.models import User


# Los modelos deben extender de models.Model
class Account(models.Model):
    # Definimos una relación 1a1 con el modelo de User para extenderlo
    # "on_delete=models.CASCADE" indica que si se borra el User, se borra el Account, y vice versa
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Campo "balance", es un campo de tipo "float", que no puede estar vacío ni nulo, y por default se pone en 0
    balance = models.FloatField(blank=False, null=False, default=0.0)


class Transaction(models.Model):
    # Usuario que origina la transacción, especificamos el nombre porque sinó tira un error
    origen = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, related_name='origen')
    # Usuario que recibe la transacción
    destino = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, related_name='destino')
    # Cantidad de dinero transferida, tendril que ser decimal field para no tener problemas de precision
    cantidad = models.FloatField(blank=False, null=False, default=0.0)
    # Fecha en que se hace la transacción
    fecha_realizada = models.DateTimeField(blank=False, null=False, auto_now_add=True)
