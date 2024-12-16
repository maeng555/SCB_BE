from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView # api사용


from smuprofile.views import ProfileList, ProfileDetail
from rest_framework.permissions import AllowAny #권한풀어주기


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # 로그인 인증을 위한 URL
    path('api/profiles/', ProfileList.as_view(), name='profile-list'),
    path('api/profiles/<int:school_id>/', ProfileDetail.as_view(), name='profile-detail'),
    #스웨거 사용하기 밑에코드
   path('schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),
]