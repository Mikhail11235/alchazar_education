from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from education.models import Course, Lection, UserTestResult


User = get_user_model()


class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.author = User.objects.create_user(username='author', password='pass')
        self.course = Course.objects.create(name='Test Course', author=self.author)
        self.lection1 = Lection.objects.create(course=self.course, title='L1', content='Content1', order=1)
        self.lection2 = Lection.objects.create(course=self.course, title='L2', content='Content2', order=2)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_course_str(self):
        self.assertEqual(str(self.course), 'Test Course')

    def test_lection_str(self):
        self.assertEqual(str(self.lection1), 'L1')

    def test_is_accessible_by_for_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.assertTrue(self.lection2.is_accessible_by(self.user))

    def test_is_accessible_by_for_author(self):
        self.assertTrue(self.lection1.is_accessible_by(self.author))

    def test_is_accessible_by_for_regular_user(self):
        self.assertTrue(self.lection1.is_accessible_by(self.user))
        self.assertFalse(self.lection2.is_accessible_by(self.user))
        UserTestResult.objects.create(user=self.user, lection=self.lection1, is_passed=True)
        self.assertTrue(self.lection2.is_accessible_by(self.user))


class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            "username": "newuser",
            "password": "newpass123",
            "teacher_name": "Teacher"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class CourseListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass')
        Course.objects.create(name='Course1', author=self.user)
        Course.objects.create(name='Course2', author=self.user)

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_courses(self):
        self.authenticate()
        url = reverse('course_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class LectionAccessTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='pass')
        self.user = User.objects.create_user(username='user', password='pass')
        self.course = Course.objects.create(name='Course1', author=self.author)
        self.lection1 = Lection.objects.create(course=self.course, title='L1', content='...', order=1)
        self.lection2 = Lection.objects.create(course=self.course, title='L2', content='...', order=2)

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_lection_detail_access(self):
        self.authenticate()
        self.client.login(username='user', password='pass')
        url = reverse('lection_detail', args=[self.lection2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        UserTestResult.objects.create(user=self.user, lection=self.lection1, is_passed=True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
