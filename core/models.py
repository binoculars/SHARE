from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(Organization, on_delete=models.DO_NOTHING)


class Email(models.Model):
    is_primary = models.Boo
    email = models.EmailField()

    def __str__(self):
        return self.email

class Affiliation(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING)

class Contributor(models.Model):
    family_name = models.CharField(max_length=200) # last
    given_name = models.CharField(max_length=200) # first
    additional_name = models.CharField(max_length=200) # can be used for middle
    suffix = models.CharField(max_length=50)

    emails = models.ManyToManyField(Email)
    # current_affiliation =
    # other_properties = models.JSONField()
    # suffix
    # non-dropping-particle
    # dropping-particle

class Manuscript(models.Model):
    title = models.CharField(max_length=200)
    doi = models.URLField()