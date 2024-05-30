"""This module provides models for the Friends app."""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Friends user model."""
    email = models.EmailField(unique=True, max_length=100)
    friends = models.ManyToManyField("User", blank=True,
                                     related_name="user_friends",
                                     )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
