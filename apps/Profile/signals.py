import random
import string

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.Accounts.models import Student, Teacher
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_unique_id():
    while True:
        random_code = "".join(random.choices(string.digits, k=6))
        new_id = f"ST-{random_code}"
        if not Student.objects.filter(student_id=new_id).exists():
            return new_id


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет связанные профили при сохранении пользователя"""
    if hasattr(instance, "student_profile"):
        instance.student_profile.save()
    if hasattr(instance, "teacher_profile"):
        instance.teacher_profile.save()