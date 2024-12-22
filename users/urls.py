from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ProfileListView

urlpatterns = [
    path('register/', RegisterView.as_view()),   # 회원가입
    path('login/', LoginView.as_view()),         # 로그인
    path('profile/', ProfileListView.as_view()),  # 전체 프로필 조회
    path('profile/<int:pk>/', ProfileView.as_view()),  # 개별 프로필 조회 및 수정
]