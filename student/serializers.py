from rest_framework import serializers
from .models import Student

student_id = serializers.CharField(required=False)
name = serializers.CharField(required=False)
age = serializers.CharField(required=False)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'