from django.db import models
from django.conf import settings

from common.models import BaseModel


class Task(BaseModel):
    create_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="작성자",
    )
    title = models.CharField(verbose_name="업무 제목", max_length=100)
    content = models.TextField(verbose_name="업무 내용", max_length=1000)

    def __str__(self) -> str:
        return f"Task(team={self.team}, is_completed={self.is_completed})"

    class Meta:
        db_table = "tasks"
        verbose_name = "업무 내역"
        verbose_name_plural = "업무 목록"
