from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.Accounts.models import Teacher
from apps.Shedule.models import Groups, Subject

User = get_user_model()


class JournalTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", role=User.Roles.STUDENT)
        self.profile = self.user.student_profile  # signal creates it
        self.profile.familiy = "Иванов"
        self.profile.name = "Иван"
        self.profile.group = Groups.objects.create(name="Test Group", course=1)
        self.profile.save()
        self.group = self.profile.group
        self.subject = Subject.objects.create(name="Test Subject")
        self.group.subjects.add(self.subject)

    def test_performance_view_redirect_for_student(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("performance"))
        self.assertRedirects(response, reverse("group_info", args=[self.group.id]))

    def test_group_info_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("group_info", args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "group_performance.html")

    def test_record_book_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("record_book"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "record_book.html")

    def test_mass_performance_update_view(self):
        teacher_user = User.objects.create_user(username="teacher", password="testpass", role=User.Roles.TEACHER)
        teacher = Teacher.objects.create(user=teacher_user, department="Факультет топлива и экологии")
        teacher.subjects.set([self.subject])
        self.client.login(username="teacher", password="testpass")
        data = {
            "date": "2023-10-01",
            "grade_1": "5",  # assuming user id 1
        }
        response = self.client.post(reverse("mass_grade", args=[self.group.id, self.subject.id]), data)
        self.assertRedirects(response, reverse("group_info", args=[self.group.id]))

    def test_performance_view_for_teacher(self):
        teacher_user = User.objects.create_user(username="teacher2", password="testpass", role=User.Roles.TEACHER)
        teacher = Teacher.objects.create(user=teacher_user, department="Факультет топлива и экологии")
        teacher.subjects.set([self.subject])

        self.client.login(username="teacher2", password="testpass")
        response = self.client.get(reverse("performance"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("group_info", args=[self.group.id])))
