from django.urls import path

from subtasks import views


urlpatterns = [
    path("/subtasks/list", views.SubTaskListView.as_view(), name="subtask_list"),
    path(
        "/tasks/<int:task_id>/subtasks",
        views.SubtaskCreateView.as_view(),
        name="subtask_create",
    ),
    path("/subtasks/<int:pk>", views.SubtaskView.as_view(), name="subtask"),
    path(
        "/subtasks/<int:pk>/completion",
        views.MarkAsCompletionView.as_view(),
        name="subtask_completion",
    ),
]
