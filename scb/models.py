from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class Profile(models.Model):
    school_id = models.IntegerField(unique=True)
    range = models.CharField(max_length=20)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Project(models.Model):
    project_id = models.CharField(max_length=20, primary_key=True)  # 프로젝트 ID
    team_name = models.CharField(max_length=30)  # 팀명
    team = models.IntegerField()  # Team
    project_code = models.CharField(max_length=20)  # 코드
    score = models.IntegerField()  # 점수
    comment = models.CharField(max_length=200)  # 댓글
    school_id = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Profile과 연관 관계

    def __str__(self):
        return self.team_name
    
class Board(models.Model):
    school_id = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Profile과 연관 관계
    title = models.CharField(max_length=20)  # 제목
    detail = models.CharField(max_length=255)  # 내용
    date = models.CharField(max_length=11)  # 날짜
    board_comment = models.CharField(max_length=255)  # 댓글

    def __str__(self):
        return self.title