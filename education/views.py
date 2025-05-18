import json
import redis
from django.conf import settings
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    User,
    Course,
    Lection,
    UserCourse,
    LectionTest,
    UserTestResult,
)
from .serializers import (
    UserRegistrationSerializer,
    CourseSerializer,
    LectionSerializer,
    UserCourseSerializer,
    UserCourseCreateSerializer,
    LectionTestSerializer,
    TestAnswersSerializer,
    LectionListSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class CourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all().order_by('id')


class LectionViewSet(viewsets.ModelViewSet):
    queryset = Lection.objects.all()
    serializer_class = LectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class EnrollCourseView(generics.CreateAPIView):
    serializer_class = UserCourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LeaveCourseView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserCourseSerializer
    queryset = UserCourse.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        return UserCourse.objects.filter(user=self.request.user)


class UserCoursesListView(generics.ListAPIView):
    serializer_class = UserCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCourse.objects.filter(user=self.request.user)


class CourseLectionsView(generics.ListAPIView):
    serializer_class = LectionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lection.objects.filter(course_id=course_id).order_by('order')


class TakeTestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TestAnswersSerializer

    def post(self, request, lection_id):
        user = request.user
        try:
            lection = Lection.objects.get(id=lection_id)
        except Lection.DoesNotExist:
            return Response({'error': 'Lection not found.'}, status=404)
        if not lection.is_accessible_by(user):
            raise PermissionDenied(
                "Access to the test is denied: previous lections must be completed."
            )
        answers = request.data.get('answers')
        tests = LectionTest.objects.filter(lection=lection)
        if not tests.exists():
            return Response({'error': 'No tests available for this lection.'}, status=404)
        if len(answers) != tests.count():
            return Response(
                {'error': 'The number of answers must match the number of questions.'},
                status=400,
            )
        score = sum(
            1 for test, answer in zip(tests, answers)
            if test.correct_answer.strip().lower() == answer.strip().lower()
        )
        passed = score == tests.count()
        test_result, _ = UserTestResult.objects.get_or_create(
            user=user, lection_id=lection_id
        )
        test_result.current_attempt_count += 1
        if test_result.current_attempt_count <= 3 and score > test_result.max_score_first_3_attempts:
            test_result.max_score_first_3_attempts = score
        if passed:
            test_result.is_passed = True
        test_result.save()
        course = tests.first().lection.course
        user_course, _ = UserCourse.objects.get_or_create(user=user, course=course)
        total_lections = Lection.objects.filter(course=course).count()
        passed_lections = UserTestResult.objects.filter(user=user, lection__course=course, is_passed=True).count()
        progress = round(passed_lections / total_lections * 100, 2)
        user_course.progress = progress
        user_course.save()
        return Response({
            'attempt_number': test_result.current_attempt_count,
            'score': score,
            'passed': passed,
            'progress': progress,
        })


class LectionDetailView(generics.RetrieveAPIView):
    queryset = Lection.objects.all()
    serializer_class = LectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not obj.is_accessible_by(user):
            raise PermissionDenied("Lection is currently unavailable.")
        return obj


class LectionTestsView(generics.ListAPIView):
    serializer_class = LectionTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lection_id = self.kwargs['lection_id']
        lection = Lection.objects.get(id=lection_id)
        user = self.request.user
        if not lection.is_accessible_by(user):
            raise PermissionDenied("Tests for this lection are not available.")
        return LectionTest.objects.filter(lection=lection)


class TopUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        data = r.get('top_10_users')
        if not data:
            return Response({"detail": "Top 10 users not found in cache."}, status=404)
        top_users = json.loads(data)
        return Response(top_users)
