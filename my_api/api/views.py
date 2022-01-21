# Create your views here.

# imports
import json

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.response import Response
from api import forms, models, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.permissions import IsAdmin
from api import constants


@api_view(['GET'])
def test_get(request):
    return Response({"hello": "world"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def test_get_path_param(request, id):
    # El parametro id se pone en los parametros de la funcion
    return Response({"hello": id}, status=status.HTTP_200_OK)


@api_view(['GET'])
def test_get_query_param(request):
    # Obtenemos el parametro 'q', y si no viene se le pone 'default'
    q = request.GET.get('q', 'default')
    return Response({"hello": q}, status=status.HTTP_200_OK)


@api_view(['POST'])
def test_post_body(request):
    # El body se encuentra en "request.data"
    return Response({"hello": request.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def test_suma(request):
    l = float(request.GET.get('l', 0))
    r = float(request.GET.get('r', 0))
    return Response({"resultado": l + r}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def test_suma_mas(request):
    aux = float(0)
    try:
        nums = json.loads(request.body.decode("utf-8"))["sums"]
    except Exception as e:
        return Response({"details": "Invalid request body"}, status=status.HTTP_400_BAD_REQUEST)
    for x in nums:
        aux = aux + x
    return Response({"resultado": aux}, status=status.HTTP_200_OK)


@api_view(['POST'])
def test_bueno(request):
    # if n_body is grater or equal to n_query returns 200 otherwise 400
    try:
        n_body = json.loads(request.body.decode("utf-8"))["n"]
        n_query = float(request.GET.get('limit', None))
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if n_body >= n_query:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def accounts_view(request):
    # Hacemos el caso de un GET y el caso de un POST
    if request.method == 'GET':
        return get_accounts(request)
    elif request.method == 'POST':
        return create_account(request)


def create_account(request):
    # Para usar las forms le pasamos el objeto "request.POST" porque esperamos que sea
    # un form que fue lanzado con un POST
    form = forms.CreateUserForm(request.POST)
    # Vemos si es válido, que acá verifica que el mail no exista ya
    if form.is_valid():
        # Guardamos el usuario que el form quiere crear, el .save() devuelve al usuario creado
        user = form.save()
        user.groups.add(Group.objects.get(name=constants.GROUP_USER))
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


def get_accounts(request):
    # Si no está autenticado, devolvemos un 401
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Obtenemos todos los usuarios y los serializamos
    users = serializers.UserSerializer(models.User.objects.all(), many=True).data
    # Agregamos los datos a la respuesta
    return Response(users, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdmin])  # Definimos que tiene que ser un admin
def user_delete(request, id):
    # No dejamos que un usuario se borre a si mismo
    if request.user.id == id:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        user = models.User.objects.get(pk=id)
        user.delete()
        # Devolvemos que no hay contenido porque lo pudimos borrar
        return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
