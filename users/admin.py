from django.contrib import admin

from .models import CustomUser  # User 모델 임포트

admin.site.register(CustomUser)  # User 모델을 admin에 등록
