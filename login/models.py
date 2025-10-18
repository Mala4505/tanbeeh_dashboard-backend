from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, tr_number, password=None, **extra_fields):
        if not tr_number:
            raise ValueError("The TR number must be set")
        user = self.model(tr_number=tr_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, tr_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(tr_number, password, **extra_fields)


class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class Hizb(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class User(AbstractBaseUser, PermissionsMixin):
    tr_number = models.CharField(max_length=10, unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    hizb = models.ForeignKey(Hizb, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    its_number = models.CharField(max_length=20)
    class_name = models.CharField(max_length=10)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'tr_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()