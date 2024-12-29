import zipfile
import requests
import io
from rest_framework.decorators import action 
from rest_framework.response import Response
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Project, Comment
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectUpdateSerializer,
    CommentSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Serializer 반환"""
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'retrieve':
            return ProjectDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        return ProjectSerializer

    @swagger_auto_schema(
        operation_description="프로젝트 목록을 조회하는 API",
        responses={
            200: openapi.Response(
                description="프로젝트 목록 반환 성공",
                schema=ProjectListSerializer(many=True),
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        """프로젝트 목록을 반환합니다."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=ProjectSerializer,
        operation_description="새로운 프로젝트를 생성하는 API",
        responses={
            201: openapi.Response(
                description="프로젝트 생성 성공",
                schema=ProjectSerializer,
            ),
            400: "유효하지 않은 요청 데이터",
        },
    )
    def create(self, request, *args, **kwargs):
        """새로운 프로젝트를 생성합니다."""
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """새로운 프로젝트를 생성합니다."""
        project = serializer.save()

        # ZIP 파일 처리 및 최상위 디렉토리 추출
        try:
            zip_data = io.BytesIO(project.code)  # BinaryField에서 ZIP 파일 데이터 가져오기
            with zipfile.ZipFile(zip_data, 'r') as zf:
                # 최상위 디렉토리 이름 추출
                top_level_dir = zf.namelist()[0].split('/')[0] if zf.namelist() else "Unknown"
                project.file_size = len(project.code)  # 파일 크기 (바이트 단위)
                project.top_level_directory = top_level_dir  # 최상위 디렉토리 이름 저장
                project.save()
        except zipfile.BadZipFile:
            project.delete()  # 잘못된 ZIP 파일 업로드 시 삭제
            raise ValueError("Invalid ZIP file uploaded.")

        # AI 모델에 점수 업데이트 요청
        self._update_project_score(project)

    def _update_project_score(self, project):
        """AI 모델로 점수 계산 및 업데이트"""
        try:
            file_data = project.code.hex()  # BinaryField 데이터를 HEX로 변환
            payload = {"code": file_data}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                "https://sozerong.pythonanywhere.com/random",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            project.score = response.json().get("score", 0.0)
        except requests.RequestException:
            project.score = 0.0
        project.save()

    @swagger_auto_schema(
        operation_description="특정 프로젝트를 조회하는 API.",
        responses={
            200: openapi.Response(
                description="프로젝트 조회 성공",
                schema=ProjectDetailSerializer,
            ),
            404: "프로젝트를 찾을 수 없음",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """특정 프로젝트를 반환합니다."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=ProjectUpdateSerializer,
        operation_description="특정 프로젝트를 수정하는 API",
        responses={
            200: openapi.Response(
                description="프로젝트 수정 성공",
                schema=ProjectUpdateSerializer,
            ),
            400: "유효하지 않은 요청 데이터",
        },
        
    )
    def partial_update(self, request, *args, **kwargs):
        """프로젝트 정보를 부분적으로 수정합니다."""
        return super().partial_update(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        """프로젝트 정보를 수정합니다."""
        partial = kwargs.pop('partial', False)  # PATCH 요청 여부 확인
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Project successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="특정 프로젝트를 삭제하는 API.",
        responses={
            204: "프로젝트 삭제 성공",
        },
    )
    def destroy(self, request, *args, **kwargs):
        """프로젝트를 삭제합니다."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Project deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="특정 프로젝트의 댓글 목록을 조회하는 API",
        responses={
            200: openapi.Response(
                description="댓글 목록 반환 성공",
                schema=CommentSerializer(many=True),
            ),
            404: "프로젝트를 찾을 수 없음",
        },
    )
    @action(detail=True, methods=['get'], url_path='comments')
    def list_comments(self, request, pk=None):
        """특정 프로젝트 댓글 목록을 조회합니다."""
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        comments = project.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CommentSerializer,
        operation_description="특정 프로젝트에 댓글을 추가하는 API",
        responses={
            201: openapi.Response(
                description="댓글 추가 성공",
                schema=CommentSerializer,
            ),
            400: "유효하지 않은 요청 데이터",
        },
    )
    @action(detail=True, methods=['post'], url_path='comments')
    def add_comment(self, request, pk=None):
        """특정 프로젝트에 댓글을 추가합니다."""
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="특정 프로젝트의 댓글을 삭제하는 API",
        manual_parameters=[
            openapi.Parameter(
                'comment_id',
                openapi.IN_PATH,
                description="댓글 ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            204: "댓글 삭제 성공",
            404: "댓글 또는 프로젝트를 찾을 수 없음",
        },
    )
    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        """특정 프로젝트의 댓글을 삭제합니다."""
        try:
            project = self.get_object()
            comment = project.comments.get(id=comment_id)
            comment.delete()
            return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="ZIP 파일안에 있는 파일을 미리볼 수 있는 API",
        responses={
            200: openapi.Response(
                description="코드 미리보기 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
                ),
            ),
            404: "프로젝트를 찾을 수 없음",
        },
    )
    @action(detail=True, methods=['get'], url_path='code-preview')
    def code_preview(self, request, pk=None):
        """ZIP 파일에서 텍스트 파일을 미리 봅니다."""
        try:
            project = Project.objects.get(pk=pk)

            zip_data = io.BytesIO(project.code)
            code_contents = {}
            with zipfile.ZipFile(zip_data, 'r') as zf:
                for file_name in zf.namelist():
                    if file_name.endswith(('.py', '.java', '.js', '.html', '.txt')):
                        with zf.open(file_name) as file:
                            code_contents[file_name] = file.read().decode('utf-8')

            return Response(code_contents, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except zipfile.BadZipFile:
            return Response({"error": "Invalid ZIP file format."}, status=status.HTTP_400_BAD_REQUEST)
