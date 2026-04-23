from django import forms
from django.contrib.auth import get_user_model
from apps.Accounts.models import Student, Teacher
from apps.Shedule.models import Faculty

User = get_user_model()

class EditProfileStudent(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['surname', 'name', 'patronymic', 'faculty',
                  'avatar', 'phone', 'group', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'group': forms.Select(attrs={'disabled': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "group" in self.fields:
            self.fields["group"].disabled = True
            self.fields["group"].required = False


class EditProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["faculty", "is_dean", "curated_group"]
        widgets = {
            "faculty": forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.Shedule.models import Groups
        
        if "curated_group" in self.fields:
            self.fields["curated_group"].queryset = Groups.objects.all()

        user = None
        if self.instance and hasattr(self.instance, 'user'):
            user = self.instance.user

        if user:
            # Не декан — скрываем is_dean и curated_group
            if not user.is_dean:
                for field in ["is_dean", "curated_group"]:
                    if field in self.fields:
                        self.fields[field].widget = forms.HiddenInput()
                        self.fields[field].required = False

            # Директор или учебный отдел — скрываем faculty
            if user.is_director or user.is_academic_office:
                if "faculty" in self.fields:
                    self.fields["faculty"].widget = forms.HiddenInput()
                    self.fields["faculty"].required = False