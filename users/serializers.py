from .models import User  # CustomUser 모델을 가져옵니다
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from .models import Profile

# 회원가입 시리얼라이저
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return {
            'user': user,
            'token': token.key  # .key로 반환
        }

    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user:
            # Token 객체가 반환되는지 확인
            token, created = Token.objects.get_or_create(user=user)
            if isinstance(token, Token):  # Token 객체인지 확인
                return {'token': token.key}  # Token 객체에서 key를 가져옵니다.
            else:
                raise serializers.ValidationError(
                    {"error": "Token creation failed."}
                )
        raise serializers.ValidationError(
            {"error": "Unable to log in with provided credentials."}
        )


class ProfileSerializer(serializers.ModelSerializer):
    # 유저명 (username)을 포함하도록 수정
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ("nickname", "range", "code", "school_id", "image","username")
    
    def validate_school_id(self, value):
        if not value:
            raise serializers.ValidationError("학번(school_id)은 필수 항목입니다.")
        return value