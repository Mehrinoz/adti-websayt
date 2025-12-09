from __future__ import annotations

from collections import defaultdict
import random

from django.db.models import Count
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Question, TestSession, TestTuri, UserAnswer, PracticeQuestion, Category


@require_GET
def test_list(request: HttpRequest) -> HttpResponse:
    """
    /tests/ - mavjud test turlari ro'yxati.
    """

    categories = TestTuri.objects.all().order_by("name")
    group_counts = (
        Question.objects.values("category_id", "group_number")
        .annotate(total=Count("id"))
        .order_by("category_id", "group_number")
    )

    groups_by_category: dict[int, list[dict]] = defaultdict(list)
    for row in group_counts:
        groups_by_category[row["category_id"]].append(
            {"group_number": row["group_number"], "total": row["total"]}
        )

    category_entries = []
    for category in categories:
        groups = groups_by_category.get(category.id, [])
        total_questions = sum(group["total"] for group in groups)
        category_entries.append(
            {
                "category": category,
                "groups": groups,
                "total_questions": total_questions,
            }
        )

    return render(
        request,
        "testapp/test_list.html",
        {"category_entries": category_entries},
    )


def _get_or_create_session_key(request: HttpRequest) -> str:
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@require_POST
def start_test(request: HttpRequest, category_id: int) -> HttpResponse:
    """
    Tanlangan TestTuriga yangi TestSession yaratadi va savol ishlash sahifasiga yuboradi.
    """

    category = get_object_or_404(TestTuri, pk=category_id)
    session_key = _get_or_create_session_key(request)

    group_number = int(request.POST.get("group_number", 1) or 1)
    if group_number < 1:
        group_number = 1

    if not Question.objects.filter(
        category=category, group_number=group_number
    ).exists():
        first_group = (
            Question.objects.filter(category=category)
            .order_by("group_number")
            .values_list("group_number", flat=True)
            .first()
        )
        if first_group is None:
            raise Http404("Ushbu kategoriya uchun savollar mavjud emas.")
        group_number = first_group

    test_session = TestSession.objects.create(
        session_key=session_key,
        category=category,
        group_number=group_number,
    )

    return redirect("test_run", test_id=test_session.pk)


@require_http_methods(["GET", "POST"])
def test_run(request: HttpRequest, test_id: int) -> HttpResponse:
    """
    /test/<test_id>/ - barcha savollar bitta sahifada ko'rsatiladi.
    POST so'rovda javoblar saqlanadi va natijalar sahifasiga yo'naltiriladi.
    """

    test_session = get_object_or_404(TestSession, pk=test_id)

    if test_session.session_key != _get_or_create_session_key(request):
        raise Http404("Ushbu test sessiyasiga kirish huquqingiz yo'q.")

    questions = list(
        Question.objects.filter(
            category=test_session.category, group_number=test_session.group_number
        ).order_by("id")
    )

    if not questions:
        return render(
            request,
            "testapp/test_empty.html",
            {"test_session": test_session},
        )

    if request.method == "POST":
        for question in questions:
            field_name = f"question_{question.id}"
            selected = (request.POST.get(field_name) or "").upper()
            if selected in {"A", "B", "C", "D"}:
                UserAnswer.objects.update_or_create(
                    test_session=test_session,
                    question=question,
                    defaults={"selected_answer": selected},
                )
            else:
                UserAnswer.objects.filter(
                    test_session=test_session, question=question
                ).delete()

        if not test_session.finished_at:
            test_session.finished_at = timezone.now()
            test_session.save(update_fields=["finished_at"])

        return redirect("test_results", test_session_id=test_session.pk)

    user_answers = {
        answer.question_id: answer.selected_answer
        for answer in UserAnswer.objects.filter(test_session=test_session)
    }

    question_entries = []
    for index, question in enumerate(questions, start=1):
        options = [
            ("A", question.choice_a),
            ("B", question.choice_b),
            ("C", question.choice_c),
            ("D", question.choice_d),
        ]
        random.shuffle(options)
        option_entries = [
            {"value": key, "text": text}
            for key, text in options
            if text not in {None, ""}
        ]

        question_entries.append(
            {
                "question": question,
                "selected": user_answers.get(question.id, ""),
                "number": index,
                "options": option_entries,
            }
        )

    total_questions = len(question_entries)

    return render(
        request,
        "testapp/test_run.html",
        {
            "test_session": test_session,
            "question_entries": question_entries,
            "total_questions": total_questions,
        },
    )


@require_GET
def test_results(request: HttpRequest, test_session_id: int) -> HttpResponse:
    """
    /results/<test_session_id>/ - natijalar sahifasi.
    """

    test_session = get_object_or_404(TestSession, pk=test_session_id)
    if test_session.session_key != _get_or_create_session_key(request):
        raise Http404()

    questions = list(
        Question.objects.filter(
            category=test_session.category, group_number=test_session.group_number
        ).order_by("id")
    )
    user_answers = {
        ua.question_id: ua.selected_answer
        for ua in UserAnswer.objects.filter(test_session=test_session)
    }

    total = len(questions)
    correct = 0
    details = []

    for q in questions:
        user_ans = user_answers.get(q.id, "")
        is_correct = user_ans == q.correct_answer
        if is_correct:
            correct += 1
        details.append(
            {
                "question": q,
                "user_answer": user_ans,
                "is_correct": is_correct,
            }
        )

    wrong = total - correct
    percentage = (correct / total * 100) if total > 0 else 0

    return render(
        request,
        "testapp/test_results.html",
        {
            "test_session": test_session,
            "group_number": test_session.group_number,
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "percentage": round(percentage, 2),
            "details": details,
        },
    )


@require_GET
def practice_questions_list(request: HttpRequest) -> HttpResponse:
    """
    /savollar/ - amaliy savollar ro'yxati.
    """
    category_slug = request.GET.get('category')
    questions = PracticeQuestion.objects.all().order_by("-created_at")
    categories = Category.objects.all()
    
    if category_slug:
        questions = questions.filter(category__slug=category_slug)
    
    return render(
        request,
        "testapp/practice_questions_list.html",
        {
            "questions": questions,
            "categories": categories,
            "current_category": category_slug
        },
    )


@require_http_methods(["GET", "POST"])
def practice_question_detail(request: HttpRequest, question_id: int) -> HttpResponse:
    """
    /savollar/<question_id>/ - savol detail va javob tekshirish.
    """
    question = get_object_or_404(PracticeQuestion, pk=question_id)
    
    user_answer = ""
    is_correct = None
    show_result = False
    
    if request.method == "POST":
        user_answer = request.POST.get("user_answer", "").strip()
        show_result = True
        if user_answer:
            # Javobni tekshirish (katta/kichik harflarni e'tiborsiz)
            is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()
        else:
            is_correct = False
    
    return render(
        request,
        "testapp/practice_question_detail.html",
        {
            "question": question,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "show_result": show_result,
        },
    )
