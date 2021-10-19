from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from datetime import timedelta
from apptrix import settings
import jwt
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,
                              null=True, default=None)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    watemark_avatar = models.ImageField(upload_to='watermark_avatars/',
                                         null=True, blank=True)
    likes = models.ManyToManyField('self', symmetrical=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = f'{self.first_name} f{self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    @property
    def token(self):
        return self._generate_jwt_token()

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
