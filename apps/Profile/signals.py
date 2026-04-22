import random
import string

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.Accounts.models import Student, Teacher

User = get_user_model()


def generate_unique_id():
    while True:
        random_code = "".join(random.choices(string.digits, k=6))
        new_id = f"ST-{random_code}"
        if not Student.objects.filter(student_id=new_id).exists():
            return new_id


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    # Если это новый пользователь со роль STUDENT и нет profile
    if created and instance.role == User.Roles.STUDENT:
        if not hasattr(instance, "student_profile"):
            Student.objects.create(user=instance, student_id=generate_unique_id())


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Если есть Student (студент), сохраняем его
    if hasattr(instance, "student_profile"):
        instance.student_profile.save()
    # Если есть Teacher (преподаватель), сохраняем его
    if hasattr(instance, "teacher_profile"):
        instance.teacher_profile.save()
