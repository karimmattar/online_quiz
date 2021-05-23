from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import validate_email
from django.db import models

from .managers import UserManager, QuestionManager, QuizManager


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, TimeStamp):
    email = models.EmailField(validators=[validate_email], max_length=255, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    # if is staff == True then user is teacher else user is student
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='media/profile', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name_plural = 'Login Information'

    def __str__(self):
        return self.email


class Question(TimeStamp):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    question_duration_in_minutes = models.IntegerField(null=False, blank=False)
    question_mark = models.IntegerField(null=False, blank=False)
    question_body = models.TextField(null=False, blank=False)
    img = models.ImageField(upload_to='media/questions', blank=True, null=True)

    objects = QuestionManager()

    class Meta:
        verbose_name_plural = 'Questions'

    def delete(self, using=None, keep_parents=False):
        if not self.author.is_staff:
            return False
        return super(Question, self).delete()

    def __str__(self):
        return '%s' % self.id


class Distraction(TimeStamp):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='distractions')
    distraction = models.CharField(max_length=160, null=False, blank=False)
    img = models.ImageField(upload_to='media/distractions', blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Distractions'

    def __str__(self):
        return '%s' % self.id


class Quiz(TimeStamp):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    enrollment_key = models.CharField(max_length=20, null=True, blank=True)
    launch_time = models.DateTimeField(null=False, blank=False)
    questions = models.ManyToManyField(Question, related_name='quiz')

    objects = QuizManager()

    class Meta:
        verbose_name_plural = 'Quizzes'

    @property
    def total_time(self):
        total = self.questions.all().aggregate(total_time=models.Sum('question_duration_in_minutes'))
        return total['total_time'] if total['total_time'] is not None else 0

    @property
    def total_mark(self):
        total = self.questions.all().aggregate(total_mark=models.Sum('question_mark'))
        return total['total_mark'] if total['total_mark'] is not None else 0

    def __str__(self):
        return '%s' % self.id


class Attendee(TimeStamp):
    enrollment_key = models.CharField(max_length=20, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendee_quizzes')

    class Meta:
        verbose_name_plural = 'Attendees'
        unique_together = ('enrollment_key', 'author')

    @property
    def check_if_corrected(self):
        for i in self.answers.all():
            if i.mark is None:
                return False
            pass
        return True

    def get_mark(self, total_mark):
        total = self.answers.all().aggregate(total_mark=models.Sum('mark'))
        mark = total['total_mark'] if total['total_mark'] is not None else 0
        return total_mark,  mark

    def __str__(self):
        return '%s' % self.id


class Answer(TimeStamp):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_answers')
    answer = models.ForeignKey(Distraction, on_delete=models.CASCADE, related_name='distraction_answers')
    mark = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Answers'

    @property
    def check_answer(self):
        write_answers = self.question.distractions.filter(is_correct=True)
        answer = self.answer
        if answer not in write_answers:
            return 0
        return self.question.question_mark

    def set_mark(self, value):
        self.mark = value

    def __str__(self):
        return '%s' % self.id
