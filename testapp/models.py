from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

# Foydalanuvchi javoblari uchun variantlar
ANSWER_CHOICES = (
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
)


## Test Turi (Test Category)
class TestTuri(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nomi')
    description = models.TextField(blank=True, verbose_name='Tavsifi')

    class Meta:
        verbose_name = 'Test turi'
        verbose_name_plural = 'Test turlari'

    def __str__(self):
        return self.name


# -------------------------------------------------------------------

## Test Savoli (Question)
class Question(models.Model):
    question_text = models.TextField(verbose_name='Savol matni')
    choice_a = models.CharField(max_length=255, verbose_name='Variant A')
    choice_b = models.CharField(max_length=255, verbose_name='Variant B')
    choice_c = models.CharField(max_length=255, verbose_name='Variant C')
    choice_d = models.CharField(max_length=255, verbose_name='Variant D')
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES, verbose_name="To'g'ri javob")
    category = models.ForeignKey(
        TestTuri,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Test turi'
    )
    # 0002_question_group_number migratsiyasidan qo'shilgan
    group_number = models.PositiveIntegerField(default=1, verbose_name="Bo'lim raqami")

    class Meta:
        verbose_name = 'Savol'
        verbose_name_plural = 'Savollar'

    def __str__(self):
        return self.question_text[:50]  # Savolning dastlabki 50 ta belgisini qaytarish


# -------------------------------------------------------------------

## Test Sessiyasi (Test Session)
class TestSession(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(
        TestTuri,
        on_delete=models.CASCADE,
        related_name='test_sessions'
    )
    # 0003_testsession_group_number migratsiyasidan qo'shilgan
    group_number = models.PositiveIntegerField(default=1)

    class Meta:
        pass  # Qo'shimcha Meta options mavjud emas

    def __str__(self):
        return f"Session {self.id} for {self.category.name}"


# -------------------------------------------------------------------

## Foydalanuvchi Javobi (User Answer)
class UserAnswer(models.Model):
    test_session = models.ForeignKey(
        TestSession,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='user_answers'
    )
    selected_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES, verbose_name='Foydalanuvchi javobi')

    class Meta:
        # Foydalanuvchi bir sessiyada bir savolga faqat bir marta javob berishi mumkin
        unique_together = (('test_session', 'question'),)

    def __str__(self):
        return f"Answer for Q{self.question.id} in Session {self.test_session.id}"


# -------------------------------------------------------------------

## Sessiya Savollari Tartibi (Session Question Order)
class SessionQuestionOrder(models.Model):
    test_session = models.ForeignKey(
        TestSession,
        on_delete=models.CASCADE,
        related_name='question_orders'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='session_orders'
    )
    # 0004_sessionquestionorder migratsiyasidan qo'shilgan, JSONField ichida savollarning tartibi saqlansa kerak.
    # Lekin bitta savol va sessiyaga biriktirilganligi sababli, bu maydon faqat bir savol uchun tartibni saqlaydi.
    # Migratsiyada bu model faqat bitta `SessionQuestionOrder` obyekti bir sessiya va bir savolga mos kelishini talab qiladi.
    order = models.JSONField(default=list)

    class Meta:
        # Bir sessiyada bir savol uchun faqat bitta tartib (order) yozuvi bo'lishi kerak.
        unique_together = (('test_session', 'question'),)

    def __str__(self):
        return f"Order for Q{self.question.id} in Session {self.test_session.id}"