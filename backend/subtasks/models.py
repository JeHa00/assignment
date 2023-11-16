from django.db import models

from common.models import BaseModel
from tasks.models import Task


class SubTask(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"SubTask(team={self.team}, is_completed={self.is_completed})"

    class Meta:
        verbose_name = "하위업무 내역"
        verbose_name_plural = "하위업무 목록"
