from rest_framework import serializers
from django.contrib.auth.models import User
from api import models, constants


# Definimos un serializer que hereda de "ModelSerializer"
class UserSerializer(serializers.ModelSerializer):
    # En Meta ponemos que el modelo es el usuario
    # Ponemos que solo queremos esos 4 campos
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_active')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ('id', 'origen', 'destino', 'cantidad', 'fecha_realizada')

#Group serializer para que no utilice el custom de django y me de mas info sensible
class GroupSerializer(serializers.Serializer):
    # Definimos que solo tiene el nombre
    name = serializers.CharField(required=True)
    # Definimos la validación
    def validate(self, data):
        if data['name'] not in [constants.GROUP_ADMIN, constants.GROUP_USER]:
            raise serializers.ValidationError(
                "Grupo Inválido")
        return data


class BalanceSerializer(serializers.Serializer):
    # Definimos que solo tiene el balance en sí
    balance = serializers.FloatField(required=True)
    # Definimos la validación
    # Validamos con el contexto que el balance no pueda ser menor que el actual
    def validate(self, data):
        if data['balance'] < self.context['user'].account.balance:
            raise serializers.ValidationError(
                "Balance invalido")
        return data


class UserDetailsSerializer(serializers.ModelSerializer):
    # Definimos los grupos con un serializer más para controlar la representación
    groups = GroupSerializer(many=True)
    # Definimos campos como read_only
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    # Definimos la account con un serializer mas para controlar la representacion
    account = BalanceSerializer(many=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'groups', 'account')
