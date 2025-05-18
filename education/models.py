from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    RANK_CHOICES = [
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Bronze', 'Bronze'),
    ]
    teacher_name = models.CharField(max_length=255)
    rank = models.CharField(max_length=10, choices=RANK_CHOICES, blank=True, null=True, default=None)

    def __str__(self):
        return self.username


class Course(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_courses')

    def __str__(self):
        return self.name


class Lection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lections')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def is_accessible_by(self, user):
        if user.is_staff or self.course.author == user:
            return True
        passed_orders = UserTestResult.objects.filter(
            user=user,
            lection__course=self.course,
            is_passed=True
        ).values_list('lection__order', flat=True)
        if not passed_orders:
            return self.order == 1
        max_passed_order = max(passed_orders)
        return self.order <= max_passed_order + 1


class LectionTest(models.Model):
    lection = models.ForeignKey(Lection, on_delete=models.CASCADE, related_name='tests')
    question = models.TextField()
    correct_answer = models.TextField()

    def __str__(self):
        return f"Test for {self.lection.title}"


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.FloatField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"


class CourseComment(models.Model):
    user_course = models.OneToOneField(UserCourse, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"Comment by {self.user_course.user.username} on {self.user_course.course.name}"


class UserTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lection = models.ForeignKey(Lection, on_delete=models.CASCADE)
    current_attempt_count = models.IntegerField(default=0)
    max_score_first_3_attempts = models.IntegerField(default=0)
    is_passed = models.BooleanField(default=False)
