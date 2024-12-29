from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated  # 로그인된 사용자만 허용
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Board, Comment
from .serializers import (
    BoardSerializer,
    BoardListSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    CommentSerializer
)
from .permissions import CustomReadOnly  # CustomReadOnly 권한 클래스를 import


class BoardViewSet(viewsets.ModelViewSet):
    """
    게시판 관련 CRUD API 제공
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [CustomReadOnly]

    @swagger_auto_schema(
        operation_description="게시판 목록 조회 API",
        responses={
            200: openapi.Response(
                "게시판 목록 반환",
                BoardListSerializer(many=True),
                examples={
                    "application/json": [
                        {"id": 1, "title": "First Board", "content": "Content of the first board"},
                        {"id": 2, "title": "Second Board", "content": "Content of the second board"}
                    ]
                }
            ),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="게시판 생성 API",
        request_body=BoardSerializer,
        responses={
            201: openapi.Response(
                "게시판 생성 성공",
                BoardSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "New Board",
                        "content": "This is the content of the new board"
                    }
                }
            ),
            400: "유효하지 않은 요청 데이터",
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="게시판 상세 조회 API",
        responses={
            200: openapi.Response(
                "게시판 상세 반환",
                BoardDetailSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "First Board",
                        "content": "Detailed content of the first board"
                    }
                }
            ),
            404: "게시판을 찾을 수 없음"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="게시판 수정 API",
        request_body=BoardUpdateSerializer,
        responses={
            200: openapi.Response(
                "게시판 수정 성공",
                BoardUpdateSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Updated Board",
                        "content": "Updated content of the board"
                    }
                }
            ),
            403: "수정 권한이 없습니다.",
            404: "게시판을 찾을 수 없음"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="게시판 삭제 API",
        responses={
            204: "게시판 삭제 성공",
            403: "삭제 권한이 없습니다.",
            404: "게시판을 찾을 수 없음"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="특정 게시판 댓글 목록 조회 API",
        responses={
            200: openapi.Response(
                "댓글 목록 반환",
                CommentSerializer(many=True),
                examples={
                    "application/json": [
                        {"id": 1, "content": "First comment", "user": "user1"},
                        {"id": 2, "content": "Second comment", "user": "user2"}
                    ]
                }
            ),
            404: "게시판을 찾을 수 없음"
        }
    )
    def list_comments(self, request, pk=None):
        return super().list_comments(request, pk=pk)

    @swagger_auto_schema(
        operation_description="특정 게시판 댓글 추가 API",
        request_body=CommentSerializer,
        responses={
            201: openapi.Response(
                "댓글 추가 성공",
                CommentSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "content": "This is a new comment",
                        "user": "user1"
                    }
                }
            ),
            400: "유효하지 않은 요청 데이터",
            404: "게시판을 찾을 수 없음"
        }
    )
    def add_comment(self, request, pk=None):
        return super().add_comment(request, pk=pk)

    @swagger_auto_schema(
        operation_description="특정 게시판 댓글 삭제 API",
        responses={
            204: "댓글 삭제 성공",
            403: "삭제 권한이 없습니다.",
            404: "댓글을 찾을 수 없음"
        }
    )
    def delete_comment(self, request, pk=None, comment_id=None):
        return super().delete_comment(request, pk=pk, comment_id=comment_id)


class CommentViewSet(viewsets.ModelViewSet):
    """
    댓글 관련 CRUD API 제공
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [CustomReadOnly]

    @swagger_auto_schema(
        operation_description="댓글 수정 API",
        request_body=CommentSerializer,
        responses={
            200: openapi.Response(
                "댓글 수정 성공",
                CommentSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "content": "Updated comment",
                        "user": "user1"
                    }
                }
            ),
            403: "수정 권한이 없습니다.",
            404: "댓글을 찾을 수 없음"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="댓글 삭제 API",
        responses={
            204: "댓글 삭제 성공",
            403: "삭제 권한이 없습니다.",
            404: "댓글을 찾을 수 없음"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
