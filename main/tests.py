from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from main.models import Profile, News, Groups  # Импортируем необходимые модели

class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Создаем пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Создаем группу
        self.group = Groups.objects.create(name='Test Group')
        
        # Создаем профиль для пользователя
        self.profile = Profile.objects.create(
            user=self.user,
            familiy='Test',
            name='User',
            group=self.group
        )

    def test_profile_view(self):
        # Аутентифицируем пользователя
        self.client.login(username='testuser', password='testpass')
        
        # Вызываем представление профиля
        response = self.client.get(reverse('profile'))
        
        # Проверяем, что ответ успешный
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что данные профиля отображаются
        self.assertContains(response, 'Test User')

class NewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Создаем пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Создаем профиль для пользователя
        self.profile = Profile.objects.create(
            user=self.user,
            familiy='Test',
            name='User',
            group=Groups.objects.create(name='Test Group')
        )
        
        # Создаем новость
        self.news = News.objects.create(
            title='Test News',
            news='This is a test news.'
        )

    def test_news_view(self):
        # Аутентифицируем пользователя
        self.client.login(username='testuser', password='testpass')
        
        # Вызываем представление новостей
        response = self.client.get(reverse('news'))
        
        # Проверяем, что ответ успешный
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что новость отображается
        self.assertContains(response, 'Test News')