from rest_framework import serializers
from .models import User, Course, Lection, LectionTest, UserCourse, UserTestResult


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'teacher_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            teacher_name=validated_data['teacher_name'],
        )
        return user


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'author']


class LectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lection
        fields = ['id', 'course', 'title', 'content']


class LectionTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectionTest
        fields = ['id', 'lection', 'question', 'correct_answer']


class UserCourseSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserCourse
        fields = ['id', 'user', 'course', 'progress', 'completed']


class UserCourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourse
        fields = ['course']


class TestAnswersSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=serializers.CharField(),
    )


class LectionListSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Lection
        fields = ['id', 'title', 'order', 'is_available']

    def get_is_available(self, obj):
        user = self.context['request'].user
        if user.is_staff or obj.course.author == user:
            return True
        passed_lections = UserTestResult.objects.filter(user=user, lection__course=obj.course, is_passed=True) \
            .values_list('lection__order', flat=True)
        if not passed_lections and obj.order == 1:
            return True
        if passed_lections and obj.order <= (max(passed_lections) + 1):
            return True
        return False
