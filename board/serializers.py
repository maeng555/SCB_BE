from rest_framework import serializers
from .models import Board, Comment
from django.contrib.auth.models import User

# 댓글 데이터를 처리하는 Serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'created_at']
        read_only_fields = ['created_at']

# Board 생성 시 사용되는 Serializer
class BoardSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='created_by.username', read_only=True)  # 'user' 필드를 읽기 전용으로 설정

    class Meta:
        model = Board
        fields = ['school_id', 'title', 'content', 'user']
        read_only_fields = ['date_created', 'date_updated']

# Board 수정 시 사용되는 Serializer
class BoardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['title', 'content']

# Board 목록 조회 시 사용되는 Serializer
class BoardListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='created_by.username', read_only=True)  # 목록에서도 'user' 필드 포함

    class Meta:
        model = Board
        fields = ['id', 'school_id', 'title', 'date_created', 'user']

# Board 상세 조회 시 사용되는 Serializer
class BoardDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'school_id',
            'title',
            'content',
            'date_created',
            'date_updated',
            'comments',
            'user'  # Board 상세 조회 시에도 'user' 필드 포함
        ]
        read_only_fields = ['date_created', 'date_updated', 'comments']