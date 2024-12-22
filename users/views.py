from .models import User
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny
from .permissions import CustomReadOnly
from .models import Profile
from rest_framework.authtoken.models import Token

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        # LoginSerializer 사용하여 유저 인증 처리
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 토큰 생성 후 반환
        token = serializer.validated_data['token']  # 수정된 부분: 'token'을 가져옴
        return Response({"token": token}, status=status.HTTP_200_OK)

class ProfileListView(generics.ListAPIView):
    # 전체 프로필 조회
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [CustomReadOnly]  # 조회는 누구나 가능

class ProfileView(generics.RetrieveUpdateAPIView):
    # 개별 프로필 조회 및 수정
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [CustomReadOnly]  # 조회는 누구나, 수정은 인증된 사용자만

    def get_object(self):
        # 개별 유저의 프로필을 반환
        return Profile.objects.get(pk=self.kwargs["pk"])

    def patch(self, request, *args, **kwargs):
        # 로그인한 유저만 자신의 프로필을 수정할 수 있게
        profile = self.get_object()
        if profile.user != request.user:
            return Response({"error": "You can only update your own profile."}, status=status.HTTP_403_FORBIDDEN)

        # 수정 처리
        return super().patch(request, *args, **kwargs)