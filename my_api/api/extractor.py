from rest_framework.response import Response
from rest_framework import status


# Extrae y valida los headers de paginación
def extract_paging_from_request(request, page_default=1, page_size_default=6):
    try:
        page = int(request.GET.get('p', page_default))
        page_size = int(request.GET.get('s', page_size_default))
    except ValueError:
        # devuelve page, size y una Response
        return None, None, Response(status=status.HTTP_400_BAD_REQUEST)
    return page, page_size, None
