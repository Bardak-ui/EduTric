from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.Accounts.models import Teacher
from .models import Groups, LessonTime, Schedule, Subject

User = get_user_model()


class SheduleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.group = Groups.objects.create(name="Test Group", course="11")
        self.subject = Subject.objects.create(name="Test Subject", teacher_name="Test Teacher")
        teacher_user = User.objects.create_user(username="teacher", password="testpass", role=User.Roles.TEACHER)
        teacher = Teacher.objects.create(user=teacher_user, department="Кафедра", is_dean=False)
        self.lesson_time = LessonTime.objects.create(lesson_number="1", start_time="09:00", end_time="10:30")
        self.schedule = Schedule.objects.create(
            group=self.group,
            subject=self.subject,
            teacher=teacher,
            weekday=1,
            lesson_time=self.lesson_time,
            room="101",
        )

    def test_schedule_creation(self):
        self.assertEqual(self.schedule.group, self.group)
        self.assertEqual(self.schedule.subject, self.subject)

    def test_groups_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("schedule"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "schedule.html")

    def test_schedule_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("schedule"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "schedule.html")

    def test_academic_office_can_add_four_pairs_each_weekday(self):
        office_user = User.objects.create_user(
            username="office", password="testpass", role=User.Roles.ACADEMIC_OFFICE
        )
        self.client.login(username="office", password="testpass")

        teacher_user = User.objects.create_user(
            username="teacher2", password="testpass", role=User.Roles.TEACHER
        )
        teacher = Teacher.objects.create(user=teacher_user, department="Кафедра", is_dean=False)

        subject = Subject.objects.create(name="Тестовый предмет", teacher_name="Преподаватель Тест")
        self.group.subjects.add(subject)
        teacher.subjects.add(subject)

        lesson_times = []
        for number, start, end in [("1", "08:30", "10:00"), ("2", "10:10", "11:40"), ("3", "11:50", "13:20"), ("4", "13:30", "15:00")]:
            lesson_times.append(LessonTime.objects.create(lesson_number=number, start_time=start, end_time=end))

        for weekday in range(1, 7):
            for lesson_time in lesson_times:
                data = {
                    "group": self.group.id,
                    "subject": subject.id,
                    "teacher": teacher.id,
                    "weekday": weekday,
                    "lesson_time": lesson_time.id,
                    "room": "101",
                }
                response = self.client.post(
                    reverse("add_schedule", args=[self.group.id]) + f"?weekday={weekday}", data
                )
                self.assertEqual(response.status_code, 302)

        self.assertEqual(Schedule.objects.filter(group=self.group).count(), 25)
