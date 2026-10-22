from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ('text', 'is_correct')


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('text', 'order')
    ordering = ('order',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'get_question_count', 'get_attempt_count', 'created_at')
    list_filter = ('is_published', 'author')
    search_fields = ('title', 'description', 'author__username')
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QuestionInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'author', 'is_published')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Вопросов')
    def get_question_count(self, obj):
        return obj.get_question_count()

    @admin.display(description='Попыток')
    def get_attempt_count(self, obj):
        return obj.get_attempt_count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text', 'quiz__title')
    ordering = ('quiz', 'order')
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'question__text')
    list_editable = ('is_correct',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'total', 'percentage', 'taken_at')
    list_filter = ('quiz', 'user')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('user', 'quiz', 'score', 'total', 'taken_at')
    ordering = ('-taken_at',)

    @admin.display(description='%')
    def percentage(self, obj):
        return f'{obj.percentage}%'
