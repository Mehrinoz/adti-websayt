from django.urls import path

from . import views

urlpatterns = [
    path("testlar/", views.test_list, name="test_list"),
    path("testlar/<int:category_id>/start/", views.start_test, name="start_test"),
    path("test/<int:test_id>/", views.test_run, name="test_run"),
    path(
        "results/<int:test_session_id>/",
        views.test_results,
        name="test_results",
    ),
    path("savollar/", views.practice_questions_list, name="practice_questions_list"),
    path("savollar/<int:question_id>/", views.practice_question_detail, name="practice_question_detail"),
]



