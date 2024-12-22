from rest_framework import serializers
from .models import Project, Comment
import base64


# 댓글 데이터를 처리하는 Serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'created_at']  # 댓글 ID, 내용, 작성자, 생성 시간 포함
        read_only_fields = ['created_at']  # 작성 시간은 읽기 전용
        ref_name = "ProjectComment"  # 고유한 참조 이름 설정



# Project 생성 시 사용되는 Serializer
class ProjectSerializer(serializers.ModelSerializer):
    code_file = serializers.FileField(write_only=True, required=True)  # ZIP 파일 업로드

    class Meta:
        model = Project
        fields = ['team_name', 'team_members', 'description', 'code_file']  # description과 code_file 포함
        read_only_fields = ['score', 'code', 'top_level_directory', 'file_size']  # 읽기 전용 필드

    def create(self, validated_data):
        # 업로드된 ZIP 파일 데이터를 code 필드에 저장
        code_file = validated_data.pop('code_file')
        validated_data['code'] = code_file.read()  # BinaryField에 ZIP 데이터 저장
        validated_data['score'] = 0  # 기본 점수 설정
        return super().create(validated_data)


# Project 수정 시 사용되는 Serializer
class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['team_name', 'team_members', 'description']  # 수정 가능한 필드만 포함


# Project 목록 조회 시 사용되는 Serializer
class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'team_name', 'team_members', 'score']  


# Project 상세 조회 시 사용되는 Serializer
class ProjectDetailSerializer(serializers.ModelSerializer):
    zip_file = serializers.CharField(source='top_level_directory', read_only=True)  # top_level_directory를 folder로 표시
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'team_name',
            'team_members',
            'description',
            'score',
            'file_size',
            'top_level_directory',
            'zip_file',
            'comments',
        ]
        read_only_fields = ['score', 'file_size', 'top_level_directory', 'comments']

'''
    def get_code(self, obj):
        """code 필드를 base64로 인코딩"""
        try:
            if obj.code:
                full_code = base64.b64encode(obj.code).decode('utf-8')
                return (
                    full_code[:50] + "..." if len(full_code) > 50 else full_code
                )  # 최대 50글자 표시
        except Exception as e:
            return f"Error encoding code: {str(e)}"
        return None
'''