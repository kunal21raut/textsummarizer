from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Summary(models.Model):
    user = models.ForeignKey(User,null = True,on_delete = models.CASCADE)
    body = models.TextField(null=True,max_length=4000)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.body