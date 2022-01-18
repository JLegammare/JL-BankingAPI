# Create your views here.

# imports
import json

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Importamos nuestros forms y modelos
from api import forms, models, serializers


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


# Esta función es la que registramos en los urls
@api_view(['POST', 'GET'])
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
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo, y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


def get_accounts(request):
    # Obtenemos todos los usuarios y los serializamos
    users = serializers.UserSerializer(models.User.objects.all(), many=True).data
    # Agregamos los datos a la respuesta
    return Response(users, status=status.HTTP_200_OK)
