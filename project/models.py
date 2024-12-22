from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Project(models.Model):
    team_name = models.CharField(max_length=100)  # 팀 이름
    team_members = models.CharField(max_length=255)  # 팀 멤버 이름 (콤마로 구분)
    code = models.BinaryField()  # ZIP 파일 데이터를 저장
    top_level_directory = models.CharField(max_length=255, blank=True)  # 최상위 디렉토리 이름 저장
    score = models.FloatField(default=0.0)  # AI 점수
    description = models.TextField(blank=True)  # 사용자 입력 내용 또는 프로젝트 설명
    created_at = models.DateTimeField(auto_now_add=True)  # default 제거
    updated_at = models.DateTimeField(auto_now=True)  # 프로젝트 수정 시간
    file_size = models.PositiveIntegerField(default=0)  # ZIP 파일 크기 (바이트 단위)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.team_name


class Comment(models.Model):
    project = models.ForeignKey(Project, related_name='comments', on_delete=models.CASCADE)  # Project와 연결
    text = models.TextField()  # 댓글 내용
    author = models.CharField(max_length=100, blank=True)  # 댓글 작성자
    created_at = models.DateTimeField(auto_now_add=True)  # 댓글 작성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 댓글 수정 시간

    def __str__(self):
        return f"Comment on {self.project.team_name} by {self.author or 'Anonymous'}"