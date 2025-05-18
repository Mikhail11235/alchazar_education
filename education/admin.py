from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Course, Lection, LectionTest, UserCourse, CourseComment, User, UserTestResult


admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(Lection)
admin.site.register(LectionTest)
admin.site.register(UserCourse)
admin.site.register(UserTestResult)
admin.site.register(CourseComment)
