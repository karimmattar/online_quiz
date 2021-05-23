from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.db.models import Manager


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password,  **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError({'email': _('The Email must be set')})
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class QuestionManager(Manager):
    def create(self, *args, **kwargs):
        if 'author' in kwargs and not kwargs['author'].is_staff:
            raise ValueError({'author': _('Author must be admin')})
        return super(QuestionManager, self).create(*args, **kwargs)

    def update(self, *args, **kwargs):
        if 'author' in kwargs and not kwargs['author'].is_staff:
            raise ValueError({'author': _('Author must be admin')})
        return super(QuestionManager, self).update(*args, **kwargs)


class QuizManager(Manager):
    def create(self, *args, **kwargs):
        if 'author' in kwargs and not kwargs['author'].is_staff:
            raise ValueError({'author': _('Author must be admin')})
        return super(QuizManager, self).create(*args, **kwargs)

    def update(self, *args, **kwargs):
        if 'author' in kwargs and not kwargs['author'].is_staff:
            raise ValueError({'author': _('Author must be admin')})
        return super(QuizManager, self).update(*args, **kwargs)
