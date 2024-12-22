from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated  # 로그인된 사용자만 허용
from rest_framework.response import Response
from rest_framework.decorators import action
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
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']  # PUT 제거
    permission_classes = [CustomReadOnly]  # CustomReadOnly 권한 클래스 적용

    def get_serializer_class(self):
        """Serializer 반환"""
        if self.action == 'list':
            return BoardListSerializer  # 목록 조회
        elif self.action == 'retrieve':
            return BoardDetailSerializer  # 상세 조회
        elif self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer  # 수정용 Serializer
        return BoardSerializer  # 기본 생성/수정 Serializer

    def perform_create(self, serializer):
        """게시판 생성 시, 현재 사용자가 작성자로 지정되도록 설정"""
        serializer.save(created_by=self.request.user)  # 'user' 필드를 'created_by'로 수정

    def perform_update(self, serializer):
        """게시판 수정 시, 현재 사용자가 작성자와 일치하는지 확인 후 수정"""
        if serializer.instance.created_by != self.request.user:
            return Response({"error": "You do not have permission to edit this board."},
                             status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """게시판 삭제 시, 현재 사용자가 작성자와 일치하는지 확인 후 삭제"""
        if instance.created_by != self.request.user:
            return Response({"error": "You do not have permission to delete this board."},
                             status=status.HTTP_403_FORBIDDEN)
        instance.delete()

    @action(detail=True, methods=['get'], url_path='comments')
    def list_comments(self, request, pk=None):
        """특정 게시물의 댓글 조회"""
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response({"error": "Board not found."}, status=status.HTTP_404_NOT_FOUND)

        comments = board.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='comments')
    def add_comment(self, request, pk=None):
        """특정 게시물에 댓글 추가"""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response({"error": "Board not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(board=board, user=request.user)  # 댓글의 user를 요청한 사용자로 설정
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        """특정 게시물의 댓글 삭제"""
        try:
            board = self.get_object()
            comment = board.comments.get(id=comment_id)
            # 댓글 삭제 권한을 검사하는 부분
            self.check_object_permissions(request, comment)  # 작성자 확인
            comment.delete()
            return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']  # PUT 제거
    permission_classes = [CustomReadOnly]  # CustomReadOnly 권한 클래스 적용

    def create(self, request, *args, **kwargs):
        """댓글 생성"""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """댓글 수정"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You do not have permission to edit this comment."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """댓글 수정(PATCH 요청 처리)"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You do not have permission to edit this comment."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """댓글 삭제"""
        instance = self.get_object()
        self.check_object_permissions(request, instance)  # 댓글의 작성자 확인
        return super().destroy(request, *args, **kwargs)