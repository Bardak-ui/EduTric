from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.Accounts.models import Student, Teacher

User = get_user_model()


class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", role=User.Roles.STUDENT)
        self.student = Student.objects.create(
            user=self.user,
            familiy="Иванов",
            name="Иван",
            otchestvo="Иванович",
            faculti="Факультет",
            student_id="12345",
        )

    def test_profile_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_edit_profile_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_profile.html")

    def test_teacher_model(self):
        teacher_user = User.objects.create_user(username="teacheruser", password="testpass", role=User.Roles.TEACHER)
        teacher = Teacher.objects.create(user=teacher_user, department="Факультет")
        self.assertEqual(str(teacher), "teacheruser — Факультет")

    def test_profile_view_redirects_teacher(self):
        teacher_user = User.objects.create_user(username="teacheruser", password="testpass", role=User.Roles.TEACHER, is_staff=True)
        Teacher.objects.create(user=teacher_user, department="Факультет")

        self.client.login(username="teacheruser", password="testpass")
        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, reverse("profile_teacher"))
