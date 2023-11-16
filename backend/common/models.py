from django.db import models


class Base(models.Model):
    class TeamChoices(models.TextChoices):
        DANBIE = "Danbie", "단비"
        DARAE = "Darae", "다래"
        BLABLA = "Blabla", "블라블라"
        CHEOLLO = "Cheollo", "철로"
        DANGI = "Dangi", "땅이"
        HAETAE = "Haetae", "해태"
        SUPI = "Supi", "수피"

    team = models.CharField(
        max_length=10,
        choices=TeamChoices.choices,
        null=False,
        blank=False,
    )
    created_at = models.DateTimeField(verbose_name="생성일", auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name="생성일", auto_now_add=True)

    class Meta:
        abstract = True


class BaseModel(Base):
    is_completed = models.BooleanField(verbose_name="완료 유무", default=False)
    completed_at = models.DateTimeField(verbose_name="완료일", auto_now=True)

    class Meta:
        abstract = True
