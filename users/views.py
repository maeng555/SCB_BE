from .models import User, Profile
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny
from .permissions import CustomReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authtoken.models import Token


class RegisterView(generics.CreateAPIView):
    """
    회원가입 API
    """
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
                        "username": "testuser",
                        "email": "testuser@example.com",
                        "password": "password123"
                    }
                },
            ),
            400: "유효하지 않은 요청 데이터",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        새로운 유저를 등록합니다.
        """
        return super().post(request, *args, **kwargs)


class LoginView(generics.GenericAPIView):
    """
    로그인 API
    """
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
        """
        유저 인증 및 토큰 반환.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 토큰 생성 후 반환
        token = serializer.validated_data['token']
        return Response({"token": token}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    개별 프로필 조회 및 수정 API
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [CustomReadOnly]

    @swagger_auto_schema(
        operation_description="개별 프로필 조회 API",
        responses={
            200: ProfileSerializer,
            404: "프로필을 찾을 수 없음",
        },
        examples={
            "application/json": {
                "username": "testuser",
                "bio": "This is the bio of the test user."
            }
        }
    )
    def get(self, request, *args, **kwargs):
        """
        특정 사용자의 프로필 정보를 조회합니다.
        """
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="개별 프로필 수정 API (PATCH 사용)",
        request_body=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            403: "수정 권한 없음",
            404: "프로필을 찾을 수 없음",
        },
        examples={
            "application/json": {
                "username": "updateduser",
                "bio": "This is an updated bio"
            }
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        로그인한 사용자가 자신의 프로필 정보를 수정합니다.
        """
        profile = self.get_object()
        if profile.user != request.user:
            return Response({"error": "You can only update your own profile."}, status=status.HTTP_403_FORBIDDEN)

        return super().patch(request, *args, **kwargs)


class ProfileListView(generics.ListAPIView):
    """
    모든 프로필 조회 API
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @swagger_auto_schema(
        operation_description="모든 프로필 조회 API",
        responses={
            200: openapi.Response(
                "프로필 리스트",
                ProfileSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "username": "user1",
                            "bio": "This is user1's bio."
                        },
                        {
                            "username": "user2",
                            "bio": "This is user2's bio."
                        }
                    ]
                }
            ),
            404: "프로필이 없습니다.",
        },
    )
    def get(self, request, *args, **kwargs):
        """
        모든 사용자의 프로필 정보를 조회합니다.
        """
        return super().get(request, *args, **kwargs)