from django.urls import path

from tasks import views


urlpatterns = [
    path("", views.TaskCreateView.as_view(), name="task_create"),
    path("/list", views.TaskListView.as_view(), name="task_list"),
    path("/tasks/<int:pk>", views.TaskView.as_view(), name="task"),
    path(
        "/tasks/<int:pk>/completion",
        views.MarkAsCompletionView.as_view(),
        name="task_completion",
    ),
]
