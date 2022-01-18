# Create your views here.

# imports
import json

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


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
    l = float(request.GET.get('l',0))
    r = float(request.GET.get('r',0))
    return Response({"resultado": l+r}, status=status.HTTP_200_OK)

@api_view(['PUT'])
def test_suma_mas(request):
    aux = float(0)
    try:
        nums = json.loads(request.body.decode("utf-8"))["sums"]
    except Exception as e:
        return  Response({"details": "Invalid request body"}, status=status.HTTP_400_BAD_REQUEST)
    for x in nums:
        aux = aux + x 
    return Response({"resultado": aux}, status=status.HTTP_200_OK)

@api_view(['POST'])
def test_bueno(request):
    #if n_body is grater or equal to n_query returns 200 otherwise 400
    try:
        n_body = json.loads(request.body.decode("utf-8"))["n"]
        n_query = float(request.GET.get('limit',None))
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if n_body >= n_query:
        return Response(status=status.HTTP_200_OK)
    else :
        return Response(status=status.HTTP_400_BAD_REQUEST)



