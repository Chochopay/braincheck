from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:pk>/publish/', views.publish_quiz, name='publish_quiz'),
    path('quiz/<int:pk>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:pk>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:pk>/results/<int:attempt_pk>/', views.quiz_results, name='quiz_results'),
    path('profile/', views.profile, name='profile'),
]
