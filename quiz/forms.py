from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Quiz


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label='Email (необязательно)')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('title', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название теста'}),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Краткое описание (необязательно)',
                'rows': 3,
            }),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
        }
