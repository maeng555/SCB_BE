import zipfile
import requests
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, Comment
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectUpdateSerializer,
    CommentSerializer
)
from .permissions import CustomReadOnly  # CustomReadOnly 권한 클래스를 import

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']  # PUT 제거
    permission_classes = [CustomReadOnly]  # CustomReadOnly 권한 클래스 적용

    def get_serializer_class(self):
        """Serializer 반환"""
        if self.action == 'list':
            return ProjectListSerializer  # 목록 조회
        elif self.action == 'retrieve':
            return ProjectDetailSerializer  # 세부사항 조회
        elif self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer  # 수정 요청 시 전용 Serializer 사용
        return ProjectSerializer  # 생성/수정용

    def perform_create(self, serializer):
        """프로젝트 생성"""
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

    def destroy(self, request, *args, **kwargs):
        """프로젝트 삭제"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Project deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """프로젝트 수정"""
        partial = kwargs.pop('partial', False)  # PATCH 요청 여부 확인
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Project successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='comments')
    def list_comments(self, request, pk=None):
        """특정 프로젝트 댓글 조회"""
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        comments = project.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='comments')
    def add_comment(self, request, pk=None):
        """특정 프로젝트에 댓글 추가"""
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        """특정 프로젝트의 댓글 삭제"""
        try:
            project = self.get_object()  # 프로젝트 객체 가져오기
            comment = project.comments.get(id=comment_id)  # 특정 댓글 가져오기
            comment.delete()  # 댓글 삭제
            return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='code-preview')
    def code_preview(self, request, pk=None):
        """ZIP 파일의 텍스트 파일 내용 미리보기"""
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