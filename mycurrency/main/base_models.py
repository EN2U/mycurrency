from django.db import models


class CodeBaseModel(models.Model):
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        abstract = True
