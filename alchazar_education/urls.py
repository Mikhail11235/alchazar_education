from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from education.views import (
    UserRegistrationView, EnrollCourseView, LeaveCourseView, UserCoursesListView,
    CourseLectionsView, LectionTestsView, TakeTestView, LectionDetailView, CourseListView, TopUsersView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/enroll/', EnrollCourseView.as_view(), name='enroll_course'),
    path('api/leave/<int:pk>/', LeaveCourseView.as_view(), name='leave_course'),
    path('api/my-courses/', UserCoursesListView.as_view(), name='my_courses'),
    path('api/courses/', CourseListView.as_view(), name='course_list'),
    path('api/courses/<int:course_id>/lections/', CourseLectionsView.as_view(), name='course_lections'),
    path('api/lections/<int:lection_id>/tests/', LectionTestsView.as_view(), name='lection_tests'),
    path('api/lections/<int:lection_id>/take-test/', TakeTestView.as_view(), name='take_test'),
    path('api/courses/<int:course_id>/lections/', CourseLectionsView.as_view(), name='course_lections'),
    path('api/lections/<int:pk>/', LectionDetailView.as_view(), name='lection_detail'),
    path('api/top-users/', TopUsersView.as_view(), name='top_users'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
