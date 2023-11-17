from django.urls import path

from tasks import views


urlpatterns = [
    path("", views.TaskListCreateView.as_view(), name="task_list_create"),
    path("/<int:pk>", views.TaskView.as_view(), name="task"),
    path(
        "/<int:pk>/completion",
        views.MarkAsCompletionView.as_view(),
        name="task_completion",
    ),
]
