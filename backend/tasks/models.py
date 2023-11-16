from django.db import models
from django.conf import settings

from common.models import BaseModel


class Task(BaseModel):
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)

    def __str__(self) -> str:
        return f"Task(team={self.team}, is_completed={self.is_completed})"

    class Meta:
        verbose_name = "업무 내역"
        verbose_name_plural = "업무 목록"
