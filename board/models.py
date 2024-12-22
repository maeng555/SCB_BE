from django.db import models
from django.contrib.auth.models import User

# 게시판 모델
class Board(models.Model):
    school_id = models.CharField("학번", max_length=10)  # 학번
    title = models.CharField("제목", max_length=100)  # 제목
    content = models.TextField("내용", null=False)  # 내용
    date_created = models.DateTimeField("작성일", auto_now_add=True, null=False)  # 작성일
    date_updated = models.DateTimeField("수정일", auto_now=True)  # 수정일

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False)  # 작성자 연결

    def __str__(self):
        return f"{self.title} ({self.school_id})"


# 댓글 모델
class Comment(models.Model):
    board = models.ForeignKey(Board, related_name='comments', on_delete=models.CASCADE, null=True)  # 게시판 연결
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # 댓글 작성자
    school_id = models.CharField("학번", max_length=10, blank=True)  # 학번
    text = models.TextField("댓글 내용", null=False)  # 댓글 내용
    created_at = models.DateTimeField("작성일", auto_now_add=True)  # 댓글 작성일
    updated_at = models.DateTimeField("수정일", auto_now=True)  # 댓글 수정일

    def save(self, *args, **kwargs):
        # 작성자의 학번을 자동으로 설정
        if self.author and not self.school_id:
            self.school_id = self.author.profile.school_id  # 프로필에서 학번 가져오기
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment on {self.board.title} by {self.author.username}"