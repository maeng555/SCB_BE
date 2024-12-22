# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.index, name='index'),  # 기본 경로 추가
# ]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, CommentViewSet

# DefaultRouter 생성
router = DefaultRouter()
router.register(r'boards', BoardViewSet)  # Board 관련 뷰셋 등록
router.register(r'comments', CommentViewSet)  # Comment 관련 뷰셋 등록

# URL 패턴 정의
urlpatterns = [
    path('', include(router.urls)),  # DefaultRouter의 URL 포함
]