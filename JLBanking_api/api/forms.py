from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
from django import forms
from . import models, constants



# Form para crear un usuario, tiene que extender a UserCreationForm esta form especial
class CreateUserForm(UserCreationForm):
    # En el meta ponemos que modelo usa
    # Y los campos que vamos a recibir,
    # deberían tener el mismo nombre que los campos del modelo
    # Password1 y Password2 son equivalentes a password y repeatPassword
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # Este método se llama cuando se trata de validar el mail
    def clean_email(self):
        try:
            # Buscamos usuarios que tengan ese mail, con el objects se acceden a todos los objetos de la db
            user = models.User.objects.get(
                email=self.cleaned_data.get('email'))
            # Si hay algún usuario, decimos que el mail ya está usado
            if user != None:
                raise ValidationError("Email already in use.")
            # Si está todo bien o no encuentra a un usuario,
            # devolvemos el email indicando que está ok
            return self.cleaned_data.get('email')
        except models.User.DoesNotExist:
            return self.cleaned_data.get('email')

# Nuestra form extiende de "Form" y no tiene un modelo asociado
class CreateTransactionForm(forms.Form):
    # Campo con el ID de la cuenta destino, no puede ser menor que 1
    destino = forms.IntegerField(min_value=1)
    # Campo para la cantidad, no puede ser menor que 0
    cantidad = forms.FloatField(min_value=0)

    def clean_destino(self):
        try:
            # Buscamos usuarios que tengan ese id
            user = models.User.objects.get(id=self.cleaned_data.get('destino'))
            # Si el usuario no es user, no dejamos que se haga
            if user == None:
                raise ValidationError("No existe el destinatario.")
            elif not user.is_active:
                raise ValidationError("No existe el destinatario.")
            elif user.groups.all()[0].name != constants.GROUP_USER:
                raise ValidationError("El destinatario no es un usuario.")
            return self.cleaned_data.get('destino')
        except models.User.DoesNotExist:
            raise ValidationError("No existe el destinatario.")