import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Quiz, Question, Choice, QuizAttempt
from .forms import QuizForm


def home(request):
    """Главная — список опубликованных тестов + мои тесты."""
    published = Quiz.objects.filter(is_published=True).select_related('author')
    my_quizzes = []
    if request.user.is_authenticated:
        my_quizzes = Quiz.objects.filter(author=request.user).select_related('author')
    return render(request, 'quiz/home.html', {
        'published': published,
        'my_quizzes': my_quizzes,
    })


@login_required
def create_quiz(request):
    """Создание нового теста."""
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.author = request.user
            quiz.save()

            # Парсим вопросы из JSON
            questions_data = request.POST.get('questions_json', '[]')
            try:
                questions = json.loads(questions_data)
            except json.JSONDecodeError:
                questions = []

            for idx, q_data in enumerate(questions):
                text = q_data.get('text', '').strip()
                if not text:
                    continue
                question = Question.objects.create(
                    quiz=quiz,
                    text=text,
                    order=idx + 1,
                )
                for c_data in q_data.get('choices', []):
                    c_text = c_data.get('text', '').strip()
                    if not c_text:
                        continue
                    Choice.objects.create(
                        question=question,
                        text=c_text,
                        is_correct=c_data.get('is_correct', False),
                    )

            messages.success(request, 'Тест создан.')
            return redirect('quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm()

    return render(request, 'quiz/create.html', {'form': form})


@login_required
def quiz_detail(request, pk):
    """Детальная страница теста (для автора)."""
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('choices')
    attempts = quiz.attempts.select_related('user')[:10]
    return render(request, 'quiz/detail.html', {
        'quiz': quiz,
        'questions': questions,
        'attempts': attempts,
    })


@login_required
@require_POST
def publish_quiz(request, pk):
    """Переключение публикации теста."""
    quiz = get_object_or_404(Quiz, pk=pk, author=request.user)
    if quiz.questions.count() == 0:
        messages.error(request, 'Нельзя опубликовать тест без вопросов.')
        return redirect('quiz_detail', pk=pk)
    quiz.is_published = not quiz.is_published
    quiz.save()
    status = 'опубликован' if quiz.is_published else 'снят с публикации'
    messages.success(request, f'Тест {status}.')
    return redirect('quiz_detail', pk=pk)


@login_required
@require_POST
def delete_quiz(request, pk):
    """Удаление теста."""
    quiz = get_object_or_404(Quiz, pk=pk, author=request.user)
    quiz.delete()
    messages.success(request, 'Тест удалён.')
    return redirect('home')


def take_quiz(request, pk):
    """Прохождение теста."""
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    questions = quiz.questions.prefetch_related('choices')

    if not questions.exists():
        messages.error(request, 'В этом тесте нет вопросов.')
        return redirect('home')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Войдите, чтобы пройти тест.')
            return redirect('login')

        score = 0
        total = questions.count()
        for question in questions:
            chosen_id = request.POST.get(f'question_{question.pk}')
            if chosen_id:
                try:
                    choice = question.choices.get(pk=int(chosen_id))
                    if choice.is_correct:
                        score += 1
                except (Choice.DoesNotExist, ValueError):
                    pass

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            score=score,
            total=total,
        )
        return redirect('quiz_results', pk=quiz.pk, attempt_pk=attempt.pk)

    return render(request, 'quiz/take.html', {
        'quiz': quiz,
        'questions': questions,
    })


def quiz_results(request, pk, attempt_pk):
    """Результаты попытки."""
    quiz = get_object_or_404(Quiz, pk=pk)
    attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, quiz=quiz)
    return render(request, 'quiz/results.html', {
        'quiz': quiz,
        'attempt': attempt,
    })


def profile(request):
    """Профиль пользователя с историей попыток."""
    if not request.user.is_authenticated:
        return redirect('login')
    attempts = QuizAttempt.objects.filter(user=request.user).select_related('quiz')[:20]
    return render(request, 'quiz/profile.html', {
        'attempts': attempts,
    })
