from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models


from common.models import BaseModel
from tasks.models import Task


class SubTask(BaseModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name="상위 업무",
        related_name="subtasks",
    )

    def __str__(self) -> str:
        return f"SubTask(team={self.team}, is_completed={self.is_completed})"

    class Meta:
        db_table = "subtasks"
        verbose_name = "하위업무 내역"
        verbose_name_plural = "하위업무 목록"


@receiver(post_save, sender=SubTask)
def detect_subtask_and_mark_as_completion(
    sender,
    instance: SubTask,
    **kwargs,
):
    task: Task = instance.task

    result = SubTask.objects.filter(task=task, is_completed=False).exists()

    if not result:
        task.is_completed = True
        task.completed_at = timezone.localtime(timezone.now())
        task.save()
