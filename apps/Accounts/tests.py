from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from apps.Shedule.models import Groups

from .forms import CustomeUserForm, ExtendedRegistrationForm
from .models import Student, Teacher

User = get_user_model()


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = Groups.objects.create(name="Test Group", course=1)

    def test_student_registration_view(self):
        data = {
            'username': 'teststudent',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': User.Roles.STUDENT,
            'familiy': 'Иванов',
            'name': 'Иван',
            'otchestvo': 'Иванович',
            'faculti': 'Факультет',
            'phone': '+123456789',
            'group': self.group.id,
            'birthday': '2000-01-01',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        user = User.objects.get(username='teststudent')
        self.assertEqual(user.role, User.Roles.STUDENT)
        student = Student.objects.get(user=user)
        self.assertEqual(student.familiy, 'Иванов')
        self.assertEqual(student.name, 'Иван')

    def test_teacher_registration_view(self):
        data = {
            'username': 'testteacher',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': User.Roles.TEACHER,
            'secure_code': 'Gt$0X1hS%_',
            'department': 'Кафедра математики',
            'is_dean': False,
            'curated_group': self.group.id,
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testteacher')
        self.assertEqual(user.role, User.Roles.TEACHER)
        teacher = Teacher.objects.get(user=user)
        self.assertEqual(teacher.department, 'Кафедра математики')


class AccountsTestCase(TestCase):
    def setUp(self):
        self.group = Groups.objects.create(name="Test Group", course=1)

    def test_register_view_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_view_post_valid(self):
        data = {
            "username": "testuser",
            "password1": "testpass123",
            "password2": "testpass123",
            "role": User.Roles.STUDENT,
            "familiy": "Иванов",
            "name": "Иван",
            "otchestvo": "Иванович",
            "faculti": "Факультет топлива и экологии",
            "group": self.group.id,
            "phone": "+1234567890",
            "birthday": "2000-01-01",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("redirect_after_login"))
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_teacher_view_get(self):
        response = self.client.get(reverse("register_teacher"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register_teacher.html")

    def test_register_teacher_view_post_valid(self):
        data = {
            "username": "testteacher",
            "password1": "testpass123",
            "password2": "testpass123",
            "department": "Кафедра математики",
            "secure_code": "Gt$0X1hS%_",
        }
        response = self.client.post(reverse("register_teacher"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("redirect_after_login"))
        self.assertTrue(User.objects.filter(username="testteacher").exists())
        # Check that user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_custom_user_form_valid(self):
        data = {
            "username": "testuser",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        form = CustomeUserForm(data)
        self.assertTrue(form.is_valid())

    def test_custom_user_form_invalid_username(self):
        data = {
            "username": "тест пользователь",  # кириллица, не разрешена
            "password1": "testpass123",
            "password2": "testpass123",
        }
        form = CustomeUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
