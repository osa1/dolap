from django.db import models

class Shelf(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True)
    #subshelves = models.ManyToManyField('self')

    def __unicode__(self):
        # return "name=%s, parent=%s" % (self.name, self.parent)
        return self.name

class User(models.Model):
    uid = models.IntegerField(primary_key=True)
    email = models.EmailField(null=True)
    display_name = models.CharField(max_length=100, null=True)
    following = models.ManyToManyField('self', null=True)

    def __unicode__(self):
        return "uid=%s" % self.uid

class File(models.Model):
    path = models.CharField(max_length=200)
    size = models.CharField(max_length=100)
    modified = models.DateTimeField()
    # modified = models.CharField(max_length=100)
    added = models.DateTimeField()
    revision = models.IntegerField()
    shelves = models.ManyToManyField(Shelf, null=True)
    mime_type = models.CharField(max_length=100)
    share_link = models.CharField(max_length=100, null=True)
    # share_expires = models.DateTimeField(null=True)
    owner = models.ForeignKey(User)
    description = models.TextField(null=True)

    def __unicode__(self):
        return "path=%s, owner=%s" % (self.path, self.owner.__unicode__())
