from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProfileSerializer
from rest_framework import status
from .models import Profile
from rest_framework.permissions import AllowAny

class ProfileList(APIView):
     permission_classes = [AllowAny]
     def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    
     def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileDetail(APIView):
     permission_classes = [AllowAny] 
     def get(self, request, school_id):
        try:
            profile = Profile.objects.get(school_id=school_id)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

     def put(self, request, school_id):
        try:
            profile = Profile.objects.filter(school_id=school_id).first()
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

     def delete(self, request, school_id):
        try:
            profile = Profile.objects.get(school_id=school_id)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)