from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('home', views.Home.as_view(), name='home'),
    path('questions', views.QuestionView.as_view(), name='questions'),
    path('questions/<int:id>/', views.QuestionView.as_view(), name='question'),
    path('questions/<int:id>/<str:_delete>/', views.QuestionView.as_view(), name='question_d'),
    path('questions/dists/update/<int:id>/<int:q_id>/', views.DistractionView.as_view(), name='dist_update'),
    path('questions/add', views.QuestionAddView.as_view(), name='question_add'),
    path('quizzes', views.QuizView.as_view(), name='quizzes'),
    path('quizzes/add', views.QuizCreationView.as_view(), name='quiz'),
    path('quizzes/<int:id>', views.QuizByIDView.as_view(), name='quiz_id'),
    path('quizzes/take', views.QuizTake.as_view(), name='quiz_take'),
    path('quizzes/answer/', views.QuizAnswer.as_view(), name='quiz_answer'),
    path('reports', views.ReportsView.as_view(), name='reports'),
    path('reports/<str:enrollment_key>', views.ReportsView.as_view(), name='reports_view_submit'),
    path('attendee/<int:id>', views.ReportByAttendeeI.as_view(), name='report_attendee_by_id'),
    path('quizzes/past', views.StudentAttendeeByID.as_view(), name='report_student_all'),
]
