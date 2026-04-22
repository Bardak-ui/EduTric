from django import forms
from django.utils import timezone
from .models import Performance

class GradeForm(forms.ModelForm):
    # Используем кортеж с пустой строкой первым элементом, 
    # чтобы поле не выбирало "5" автоматически, если оценка еще не стоит
    GRADE_CHOICES = [
        ("", "---"), 
        ("5", "5"),
        ("4", "4"),
        ("3", "3"),
        ("2", "2"),
        ("Н", "Н (Отсутствие)"),
    ]

    # Переносим определение внутрь Meta или оставляем здесь, 
    # но добавляем обязательный атрибут choices
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES, 
        label="Оценка/Явка",
        widget=forms.Select(attrs={'class': 'form-select'}) # form-select лучше подходит для <select> в Bootstrap 5
    )
    
    date = forms.DateField(
        label="Дата",
        initial=timezone.now,
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = Performance
        fields = ["grade", "date"]

    # Опционально: проверка, чтобы дату не ставили в будущем
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date > timezone.now().date():
            raise forms.ValidationError("Нельзя ставить оценку будущим числом!")
        return date