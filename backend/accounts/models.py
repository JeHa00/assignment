from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models

from common.models import Base


class UserManager(BaseUserManager):
    def _create_user(
        self,
        username: str,
        password: str,
        is_staff: bool,
        is_superuser: bool,
        **extra_fields,
    ):
        if not username or not password:
            raise ValueError("username과 password는 반드시 입력해야 합니다.")

        user: User = self.model(
            username=username,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username: str, password: str, **extra_fields):
        return self._create_user(username, password, False, False, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True, **extra_fields)


class User(AbstractBaseUser, Base):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return f"User(username={self.username}, team={self.team})"

    class Meta:
        verbose_name = "직원"
        verbose_name_plural = "직원 목록"
