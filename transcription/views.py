# some views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def welcome_view(request):
    return Response({"message": "Base root: V1.0"})