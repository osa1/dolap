from django.db import models

class Shelf(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True)
    #subshelves = models.ManyToManyField('self')

class User(models.Model):
    uid = models.IntegerField(primary_key=True)

class File(models.Model):
    path = models.CharField(max_length=200)
    size = models.CharField(max_length=100)
    # modified = models.DateTimeField()
    modified = models.CharField(max_length=100)
    revision = models.IntegerField()
    shelves = models.ManyToManyField(Shelf, null=True)
    mime_type = models.CharField(max_length=100)
    owner = models.ForeignKey(User)
    description = models.TextField(null=True)
