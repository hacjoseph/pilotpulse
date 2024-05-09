from django.db import models
from fitbit.models import FitbitUser
import os

class Pilote(models.Model):
    
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    ]
    
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    age = models.IntegerField()
    experience = models.IntegerField(default=0)
    photo = models.ImageField(upload_to="pilote_photos/", height_field=None, width_field=None, max_length=None, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    fitbit_user = models.ForeignKey(FitbitUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='pilotes')
    def __str__(self):
        return f"{"prenom":self.prenom} {"nom":self.nom}"


