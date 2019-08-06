from django.db import models

# Create your models here.
class CDriveUser(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    email = models.EmailField(max_length=70)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
