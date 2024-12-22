from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

class BoardList(APIView) :
    
    def get(self, request):

        model = Board.objects.all()
        serializer = BoardSerializer(model, many=True)
        return Response(serializer.data)
    
    def post(self, request):

        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid() :
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetail(APIView) :
    def get(self, request, id):

        model = Board.objects.get(id=id)
        serializer = BoardSerializer(model)
        return Response(serializer.data)
    

    def put(self, request, id):

        model = Board.objects.get(id=id)
        serializer = BoardSerializer(model, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):

        model = Board.objects.get(id=id)
        model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)