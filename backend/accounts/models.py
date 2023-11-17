from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models

from common.models import Base


class UserManager(BaseUserManager):
    def create_user(self, username: str, password: str, **kwargs):
        if not username:
            raise ValueError("Please enter your username")
        if not password:
            raise ValueError("Please enter your password")

        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, Base):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        blank=False,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    USERNAME_FIELD = "username"
    objects = UserManager()

    def __str__(self) -> str:
        return f"User(username={self.username}, team={self.team})"

    class Meta:
        verbose_name = "직원"
        verbose_name_plural = "직원 목록"
