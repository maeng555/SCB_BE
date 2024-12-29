from django.contrib.auth.models import User
from .models import Profile  # Profile이 users 앱의 models.py에 정의되어 있다고 가정
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny
from .permissions import CustomReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authtoken.models import Token

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="회원가입 API",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                "회원가입 성공",
                RegisterSerializer,
                examples={
                    "application/json": {
                        "username": "202021058",  # 학번 예시
                        "email": "testuser@example.com",
                        "password": "password123"
                    }
                },
            ),
            400: "유효하지 않은 요청 데이터",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="로그인 API",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                "로그인 성공, 토큰 반환",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING, description="인증 토큰")
                    },
                ),
                examples={
                    "application/json": {
                        "token": "abc123xyz456"
                    }
                }
            ),
            400: "유효하지 않은 요청 데이터",
            401: "인증 실패",
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        return Response({"token": token}, status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [CustomReadOnly]

    @swagger_auto_schema(
        operation_description="개별 프로필 조회 API",
        responses={
            200: ProfileSerializer,
            404: "프로필을 찾을 수 없음",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="개별 프로필 수정 API (PATCH 사용)",
        request_body=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            403: "수정 권한 없음",
            404: "프로필을 찾을 수 없음",
        },
    )
    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user:
            return Response({"error": "You can only update your own profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

class ProfileListView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @swagger_auto_schema(
        operation_description="모든 프로필 조회 API",
        responses={
            200: openapi.Response(
                "프로필 리스트",
                ProfileSerializer(many=True),
            ),
            404: "프로필이 없습니다.",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# 수정 사항
# 1. `school_id` 관련 로직 및 설명 제거.
# 2. 모든 API에서 username을 학번으로 다룰 수 있도록 예시 업데이트.