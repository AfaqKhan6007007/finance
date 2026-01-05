from django.db import models

class Login(models.Model):
    email = models.EmailField(max_length=56,null=True)
    password = models.CharField(max_length=56)

class Signup(models.Model):
    first_name = models.CharField(max_length=56,null=True)
    last_name = models.CharField(max_length=56,null=True)
    username = models.CharField(max_length=56,null=True)
    email = models.EmailField(max_length=56,null=True)
    password = models.CharField(max_length=56)
    confirm_password = models.CharField(max_length=56)

# Create your models here.
