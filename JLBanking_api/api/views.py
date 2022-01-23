# Create your views here.

# imports
import json

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from api.permissions import IsAdmin, IsUser, IsOwner
from api import forms, models, serializers, constants, pagination, extractor, mailing
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode


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
        # commit en false para que espere para guardarlo en la base de datos
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        user.groups.add(Group.objects.get(name=constants.GROUP_USER))
        # Creamos la Account que va con el usuario, y le pasamos el usuario que acabamos de crear
        models.Account.objects.create(user=user)
        # enviamos el mail
        mailing.send_confirmation_email(user, request)
        # Respondemos con los datos del serializer, le pasamos nuestro user y le decimos que es uno solo,
        # y depués nos quedamos con la "data" del serializer
        return Response(serializers.UserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


def get_accounts(request):
    # Chequear que no sea anónimo
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # Extraemos el query param, ponemos None como default
    query = request.GET.get('q', None)
    # Extraemos los query de paginación, y si hay un error devolvemos eso
    page, page_size, err = extractor.extract_paging_from_request(request=request)
    if err is not None:
        return err

    # Si hay query, agregamos el filtro, sino usa todos
    if query != None:
        # Hacemos icontains sobre el username, y ordenamos por id, el "-" indica que es descendiente
        queryset = models.User.objects.filter(
            username__icontains=query).order_by('-id')
    else:
        # Definimos el set como todos los usuarios
        queryset = models.User.objects.all().order_by('-id')

    # Usamos un try catch por si la página está vacía
    try:
        # Convertimos a Paginator
        query_paginator = Paginator(queryset, page_size)
        # Nos quedamos con la página que queremos
        query_data = query_paginator.page(page)
        # Serializamos a los usuarios
        serializer = serializers.UserSerializer(query_data, many=True)
        # Agregamos a los usuarios a la respuesta
        resp = Response(serializer.data, status=status.HTTP_200_OK)
        # Agregamos headers de paginación a la respuesta
        resp = pagination.add_paging_to_response(
            request, resp, query_data, page, query_paginator.num_pages)
        return resp
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE', 'GET', 'PUT'])
@permission_classes([IsOwner | IsAdmin])
def user_specific_view(request, id):
    if request.method == 'GET':
        return get_user(request, id)
    elif request.method == 'PUT':
        return user_update(request, id)
    else:
        return user_delete(request, id)


# CON PUT se reemplaza la entidad entera en la base de datos
def user_update(request, id):
    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        user = models.User.objects.get(pk=id)
        # Creamos el serializer, con el context como el user
        serializer = serializers.UserDetailsSerializer(data=request.data, context={'user': user})
        # Vemos que sea válido, sinó damos error
        if serializer.is_valid():
            # En caso que sea el usuario, permitimos el cambio de balance
            if request.user.groups.all()[0].name == constants.GROUP_USER:
                # Cambiamos balance, accedemos así porque como usamos un "source" en el campo
                # Al recibirlo lo toma en la jerarquía del "source" que habíamos definido
                user.account.balance = serializer.validated_data.get('account')['balance']
                # Guardamos
                user.account.save()
            else:
                # Vemos que no se saque el rol a sí mismo
                if id == request.user.id and serializer.groups[0].name != constants.GROUP_ADMIN:
                    return Response({"Error": "No se puede cambiar el propio rol"}, status=status.HTTP_400_BAD_REQUEST)
                # Recuperamos el nuevo rol, accedemos así porque el objeto es un OrderedDic
                group = Group.objects.get(name=serializer.validated_data.get('groups')[0].get('name'))
                # Cambiamos balance, accedemos así porque como usamos un "source" en el campo
                # Al recibirlo lo toma en la jerarquía del "source" que habíamos definido
                user.account.balance = serializer.validated_data.get('account')['balance']
                # Sacamos roles actuales
                user.groups.clear()
                # Agregamos el nuevo rol
                user.groups.add(group)
                # Guardamos
                user.account.save()
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)


def get_user(request, id):
    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        # Buscamos al usuario por ID
        user = models.User.objects.get(pk=id)
        # Serializamos al user
        return Response(serializers.UserDetailsSerializer(user, many=False).data, status=status.HTTP_200_OK)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)


def user_delete(request, id):
    # No dejamos que un usuario se borre a si mismo
    # Vemos si el ID del usuario de la request es igual al que se manda en la URL
    # Vemos de asegurarnos que sea un admin
    if request.user.id == id:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.user.groups.all()[0].name != constants.GROUP_ADMIN:
        return Response(status=status.HTTP_403_FORBIDDEN)

    # Necesitamos un try-catch porque tal vez el usuario no existe
    try:
        # Buscamos al usuario por ID
        user = models.User.objects.get(pk=id)
        # Hacemos que no esté activo en vez de borrado físico
        user.is_active = False
        user.save()
        # Devolvemos que no hay contenido porque lo pudimos borrar
        return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        # Si no existe le damos un 404
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'GET'])
@permission_classes([IsUser])
def transaction_view(request):
    if request.method == 'POST':
        return create_transaction(request)
    else:
        return get_transactions(request)


def get_transactions(request):
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    inicio, fin, err = extractor.extract_limits_from_request(request=request)
    print(str(inicio))
    print(str(fin))
    if err != None:
        return err

    page, page_size, err = extractor.extract_paging_from_request(request=request)

    if err != None:
        return err

    if inicio != None and fin != None:
        # Hacemos 2 filtros, primero vemos transacciones del usuario en donde es destino u origen
        # Después filtramos por fechas y ordenamos por id descendente
        queryset = models.Transaction.objects.filter(
            (Q(destino=request.user) | Q(origen=request.user)), fecha_realizada__range=(inicio, fin)).order_by('-id')
    else:
        # Hacemos 1 solo filtro, con transacciones del usuario
        queryset = models.Transaction.objects.filter(
            (Q(destino=request.user) | Q(origen=request.user))).order_by('-id')

    try:
        transactions_paginator = Paginator(queryset,page_size)
        transactions_page = transactions_paginator.page(page)
        serializer = serializers.TransactionSerializer(transactions_page,many=True)
        resp = Response(serializer.data, status=status.HTTP_200_OK)
        resp = pagination.add_paging_to_response(
            request, resp, transactions_page, page, transactions_paginator.num_pages)
        return resp
    except EmptyPage:
        return Response(status=status.HTTP_404_NOT_FOUND)


def create_transaction(request):
    # Creamos el form
    form = forms.CreateTransactionForm(request.POST)
    # Vemos si es válido
    if form.is_valid():
        # No se chequea el usuario destino porque eso se valida en el form
        destino = models.User.objects.get(id=form.cleaned_data['destino'])
        cantidad = form.cleaned_data['cantidad']
        # Usamos un bloque transaccional para evitar problemas
        try:
            with transaction.atomic():
                # Vemos que tenga plata suficiente
                if cantidad > request.user.account.balance:
                    return Response({"error": "Balance insuficiente"}, status=status.HTTP_400_BAD_REQUEST)
                # Creamos la transaccion
                tx = models.Transaction(origen=request.user, destino=destino, cantidad=cantidad)
                # Actualizamos los balances
                request.user.account.balance -= cantidad
                destino.account.balance += cantidad
                # Guardamos los cambios
                tx.save()
                request.user.account.save()
                destino.account.save()
                # Nuestra respuesta
                return Response(serializers.TransactionSerializer(tx, many=False).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "Error transfiriendo fondos"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, uidb64, token):
    try:
        # Extraemos user id y recuperamos al usuario
        uid = urlsafe_base64_decode(uidb64).decode()
        user = models.User.objects.get(pk=uid)
        # Verificamos el token
        if user != None and default_token_generator.check_token(user, token):
            # Marcamos como activo
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except models.User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)
