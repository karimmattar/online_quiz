from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, Question, Distraction, Quiz


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'is_active')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class DistractionForm(forms.ModelForm):
    distraction = forms.CharField(required=True, label='',
                                  widget=forms.TextInput(attrs={'class': 'text-right'}))
    is_correct = forms.BooleanField(required=False, label='إجابة صحيحة',
                                    widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Distraction
        fields = (
            'id', 'distraction', 'is_correct'
        )
        read_only = ('id',)


class QuestionForm(forms.ModelForm):
    question_duration_in_minutes = forms.IntegerField(required=True, label='المدة', widget=forms.NumberInput(
        attrs={'class': "text-right"}), help_text='مدة السؤال بالدقائق')
    question_mark = forms.IntegerField(required=True, label='الدرجة', widget=forms.NumberInput(
        attrs={'class': "text-right"}))
    question_body = forms.CharField(required=True, label='السؤال',
                                    widget=forms.Textarea(attrs={'class': 'text-right', 'rows': '5'}),
                                    help_text='هذا الحقل يمكن ان يتعدي ال 160 حرف')
    img = forms.ImageField(required=False, label='الصورة',
                           help_text='لحذف الصورة اضغط علي clear و لتعديل الصورة اضغط علي choose file')

    class Meta:
        model = Question
        fields = (
            'id', 'question_duration_in_minutes', 'question_mark', 'question_body', 'img'
        )
        read_only = ('id',)


class QuizForm(forms.Form):
    enrollment_key = forms.CharField(
        required=True, label='مفتاح الأنضمام', widget=forms.TextInput(attrs={
            'class': 'text-right'
        }), help_text='مفتاح الإنضمام'
    )
    launch_time = forms.DateTimeField(required=True, label='وقت الإقلاع', widget=forms.DateTimeInput(
        attrs={'class': 'text-right datetimepicker-input'}
    ), help_text='الوقت المحدد لإقلاع الإختبار')
    questions = forms.MultipleChoiceField(required=True, label='الأسئلة')

# class QuestionAddForm(forms.Form):
#     question_duration_in_minutes = forms.IntegerField(required=True, label='المدة', widget=forms.NumberInput(
#         attrs={'class': "text-right"}), help_text='مدة السؤال بالدقائق')
#     question_mark = forms.IntegerField(required=True, label='الدرجة', widget=forms.NumberInput(
#         attrs={'class': "text-right"}))
#     question_body = forms.CharField(required=True, label='السؤال',
#                                     widget=forms.Textarea(attrs={'class': 'text-right', 'rows': '5'}),
#                                     help_text='هذا الحقل يمكن ان يتعدي ال 160 حرف')
#     img = forms.ImageField(required=False, label='الصورة',
#                            help_text='لحذف الصورة اضغط علي clear و لتعديل الصورة اضغط علي choose file')
