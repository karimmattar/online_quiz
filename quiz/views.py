import datetime
import json

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from .decorators import is_auth_user, is_staff
from .forms import QuestionForm, DistractionForm, QuizForm
from .models import Question, Distraction, Quiz, Attendee, Answer

User = get_user_model()


class Login(View):
    template_name = 'quiz/login.html'
    template_title = 'login'

    @method_decorator(is_auth_user)
    def post(self, request, **kwargs):
        if 'email' not in request.POST and 'password' not in request.POST:
            messages.error(request, 'يرجي التأكد من ادخال البريد الإلكتروني و كلمة المرور')
            return render(request, self.template_name, {'title': self.template_title})
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.error(request, 'هذا المستخدم غير مسجل, يرجي التسجيل و إعادة المحاولة')
            return render(request, self.template_name, {'title': self.template_title})

        if not user.check_password(password):
            messages.error(request, 'كلمة المرور خاظئة')
            return render(request, self.template_name, {'title': self.template_title})
        login(request, user)
        return redirect('home')

    @method_decorator(is_auth_user)
    def get(self, request, **kwargs):
        return render(request, self.template_name, {'title': self.template_title})


class Logout(View):
    def get(self, request, **kwargs):
        logout(request)
        return redirect('login')


class Home(View):
    template_name = 'quiz/home.html'
    template_title = 'Home'

    @method_decorator(login_required)
    def get(self, request):
        return render(request, self.template_name, {'title': self.template_title})


class QuestionView(View):
    template_name = 'quiz/questions.html'
    single_template_name = 'quiz/question.html'
    template_title = 'Questions'
    single_template_title = 'Question'
    form_class = QuestionForm
    dists_form_class = DistractionForm

    @method_decorator(login_required, is_staff)
    def get(self, request, id=None, _delete=None):
        if id is None and _delete is None:
            questions = Question.objects.filter(author=request.user).order_by('-created_at')
            return render(request, self.template_name, {
                'title': self.template_title,
                'questions': questions
            })
        try:
            question = Question.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم العثور علي هذا العنصر')
            return redirect('questions')
        if _delete is None and id is not None:
            distractions = question.distractions.all()
            forms = [{'form': DistractionForm(instance=i), 'id': i.id} for i in distractions]
            return render(request, self.single_template_name, {
                'title': self.single_template_title,
                'form': self.form_class(instance=question),
                'id': question.id, 'forms': forms
            })
        question.delete()
        messages.success(request, 'تم حذف عنصر بنجاح')
        return redirect('questions')

    @method_decorator(login_required, is_staff)
    def post(self, request, id):
        try:
            question = Question.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم العثور علي هذا العنصر')
            return redirect('questions')
        form = self.form_class(data=request.POST, files=request.FILES, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل عنصر بنجاح')
            return redirect('question', question.id)
        messages.warning(request, 'تم ادخال بيانات خاطئة, حاول مرة أخري')
        return redirect('question', question.id)


class DistractionView(View):
    form_class = DistractionForm

    @method_decorator(login_required, is_staff)
    def post(self, request, id, q_id=None):
        try:
            dist = Distraction.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم ايجاد العنصر')
            if q_id is not None:
                return redirect('question', q_id)
            return redirect('questions')
        form = self.form_class(data=request.POST, instance=dist)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل العنصر بنجاح')
            if q_id is not None:
                return redirect('question', q_id)
            return redirect('questions')
        if q_id is not None:
            return redirect('question', q_id)
        return redirect('questions')

    @method_decorator(login_required, is_staff)
    def get(self, request, id, q_id=None):
        try:
            dist = Distraction.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم ايجاد العنصر')
            if q_id is not None:
                return redirect('question', q_id)
            return redirect('questions')
        question = Question.objects.get(id=id)
        if question.distractions.all().count() <= 2:
            messages.warning(request, 'الحد الأدني من الأختيارات يجب ان يكوم 2')
            return redirect('question', q_id)
        dist.delete()
        messages.success(request, 'تم حذف عنصر بنجاح')
        if q_id is not None:
            return redirect('question', q_id)
        return redirect('questions')


class QuestionAddView(View):
    template_name = 'quiz/question_add.html'
    template_title = 'Add question'
    form_class = QuestionForm
    dists_model_class = Distraction

    @method_decorator(login_required, is_staff)
    def get(self, request):
        # data = request.GET
        # if 'choices_dists' in data:
        #     nn = [json.loads(i) for i in json.loads(data['choices_dists'])]
        #     print(nn)
        form = self.form_class()
        return render(request, self.template_name, {
            'title': self.template_title, 'form': form
        })

    @method_decorator(login_required, is_staff)
    def post(self, request):
        form = self.form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                form.save(commit=False)
                question_duration_in_minutes = form.cleaned_data['question_duration_in_minutes']
                question_mark = form.cleaned_data['question_mark']
                question_body = form.cleaned_data['question_body']
                img = form.cleaned_data['img']
                question = Question.objects.create(
                    author=request.user, question_duration_in_minutes=question_duration_in_minutes,
                    question_mark=question_mark, question_body=question_body, img=img
                )
                choices_dists = [json.loads(i) for i in json.loads(request.POST['choices_dists'])]
                for item in choices_dists:
                    Distraction.objects.create(
                        question=question, distraction=item['value'], is_correct=item['is_correct']
                    )
                messages.success(request, 'تم إضافة العنصر بنجاح')
            except Exception as e:
                print(e)
                messages.error(request, 'حدث خطأ عند إضافة العنصر')
            return redirect('questions')
        return redirect('question_add')


class QuizView(View):
    model_class = Quiz
    template_name = 'quiz/upcoming_quizzes.html'
    template_title = 'upcoming quizzes'

    @method_decorator(login_required, is_staff)
    def get(self, request):
        user = request.user
        now = timezone.now()
        upcoming = self.model_class.objects.filter(author=user).order_by('launch_time')
        return render(request, self.template_name, {
            'title': self.template_title, 'quizzes': upcoming
        })


class QuizCreationView(View):
    model_class = Quiz
    template_name = 'quiz/quiz_create.html'
    template_title = 'create quiz'
    form_class = QuizForm

    @method_decorator(login_required, is_staff)
    def get(self, request):
        user = request.user
        qus = user.questions.all()
        return render(request, self.template_name, {
            'title': self.template_title, 'qus': qus
        })

    def post(self, request):
        data = request.POST
        user = request.user
        qus = user.questions.all()
        try:
            data['enrollment-key']
        except Exception:
            messages.error(request, 'تأكد من توليد مفتاح انضمام')
            return render(request, self.template_name, {
                'title': self.template_title, 'qus': qus
            })
        try:
            data['questions']
        except Exception:
            messages.error(request, 'تأكد من ادخال سؤال واحد علي الاقل')
            return render(request, self.template_name, {
                'title': self.template_title, 'qus': qus
            })
        date = data['launch-time-date']
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'تأكد من ادخال التنسيق التالي YYYY-MM-DD HH:MM')
            return render(request, self.template_name, {
                'title': self.template_title, 'qus': qus
            })
        date = date.split('-')
        time = data['launch-time-time'].split(':')
        DT = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[-1]), hour=int(time[0]),
                               minute=int(time[-1]))
        questions = Question.objects.filter(id__in=list(map(int, dict(data)['questions'])))
        try:
            quiz = Quiz.objects.create(
                author=user, enrollment_key=data['enrollment-key'], launch_time=DT
            )
            quiz.questions.add(*questions)
            quiz.save()
        except Exception as e:
            print(e)
            messages.error(request, e)
            return render(request, self.template_name, {
                'title': self.template_title, 'qus': qus
            })
        return redirect('quizzes')


class QuizByIDView(View):
    model_class = Quiz
    template_name = 'quiz/quiz_view.html'
    template_title = 'view quiz'

    @method_decorator(login_required, is_staff)
    def get(self, request, id):
        try:
            quiz = self.model_class.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم ايجاد العنصر')
            return redirect('quizzes')
        return render(request, self.template_name, {
            'title': self.template_title, 'quiz': quiz
        })


class QuizTake(View):
    model_class = Quiz
    template_name = 'quiz/quiz_take.html'
    template_title = 'take quiz'

    @method_decorator(login_required, is_auth_user)
    def get(self, request):
        return render(request, self.template_name, {
            'title': self.template_title
        })

    @method_decorator(login_required, is_auth_user)
    def post(self, request):
        user = request.user
        enrollment_key = request.POST['enrollment']
        try:
            quiz = self.model_class.objects.get(enrollment_key=enrollment_key)
        except ObjectDoesNotExist:
            messages.error(request, 'مفتاح غير صحيح')
            return render(request, self.template_name, {
                'title': self.template_title
            })
        now = timezone.now()
        if quiz.launch_time > now:
            messages.error(request, 'الموعد لم يحين بعد')
            return render(request, self.template_name, {
                'title': self.template_title
            })
        if quiz.launch_time + timezone.timedelta(minutes=quiz.total_time) < now:
            messages.error(request, 'انتهت صلاحية الاختبار')
            return render(request, self.template_name, {
                'title': self.template_title
            })
        try:
            Attendee.objects.get(author=user, enrollment_key=enrollment_key)
        except ObjectDoesNotExist:
            attendee = Attendee.objects.create(
                enrollment_key=enrollment_key, author=user
            )
            return render(request, 'quiz/quiz_answers.html', {
                'title': 'quiz answers', 'quiz': quiz,
                'attendee_id': attendee.id
            })
        messages.error(request, 'تم التسجيل مسبقا')
        return redirect('quiz_take')


class QuizAnswer(View):

    @method_decorator(login_required, is_auth_user)
    def post(self, request):
        data = dict(request.POST)
        data.pop('csrfmiddlewaretoken')
        attendee_id = data.pop('attendee_id')
        values = [i[-1] for i in data.values()]
        distractions = Distraction.objects.filter(id__in=values)
        attendee = Attendee.objects.get(id=int(attendee_id[-1]))
        for dist in distractions:
            Answer.objects.create(
                attendee=attendee, question=dist.question, answer=dist
            )
        messages.success(request, 'تهانينا تم الانتهاء من الاختبار')
        return redirect('home')


class ReportsView(View):
    template_name = 'quiz/reports.html'
    template_title = 'reports'

    @method_decorator(login_required, is_staff)
    def get(self, request, enrollment_key=None):
        user = request.user
        if enrollment_key:
            attendees = Attendee.objects.filter(enrollment_key=enrollment_key)
            return render(request, 'quiz/report_view_submit.html', {
                'title': self.template_title, 'attendees': attendees
            })
        quizzes = user.quizzes.all().order_by('launch_time')
        return render(request, self.template_name, {
            'title': self.template_title, 'quizzes': quizzes
        })


class ReportByAttendeeI(View):
    template_name = 'quiz/report_by_user_id.html'
    template_title = 'report view'

    @method_decorator(login_required, is_staff)
    def get(self, request, id):
        try:
            attendee = Attendee.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم ايجاد العنصر')
            return redirect('reports')
        try:
            quiz = Quiz.objects.get(enrollment_key=attendee.enrollment_key)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم ايجاد العنصر')
            return redirect('reports')
        total_mark, mark = attendee.get_mark(quiz.total_mark)
        return render(request, self.template_name, {
            'title': self.template_title, 'attendee': attendee, 'total_mark': total_mark, 'mark': mark
        })

    @method_decorator(login_required, is_staff)
    def post(self, request, id):
        try:
            attendee = Attendee.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'لم يتم ايجاد العنصر')
            return redirect('reports')
        for i in attendee.answers.all():
            answer = i.check_answer
            print(answer)
            i.set_mark(answer)
            i.save()
        return redirect('report_attendee_by_id', id)


class StudentAttendeeByID(View):
    template_name = 'quiz/report_student_all.html'
    template_title = 'view past quizzes'

    @method_decorator(login_required, is_auth_user)
    def get(self, request):
        user = request.user
        attendees = Attendee.objects.filter(author=user)
        quizzes = Quiz.objects.filter(enrollment_key__in=attendees.values('enrollment_key'))
        list_out_put = []
        for i in attendees:
            total_mark = quizzes.filter(enrollment_key=i.enrollment_key).last().total_mark
            mark, total = i.get_mark(total_mark)
            list_out_put.append({
                'total_mark': total,
                'mark': mark,
                'key': i.enrollment_key
            })
        return render(request, self.template_name, {
            'title': self.template_title, 'attendees': list_out_put
        })
