from django.db import models
from pilotes.models import Pilote

class Experimentation(models.Model):
    nom = models.CharField(max_length=100)
    date = models.DateField()
    temps_debut = models.TimeField()
    temps_fin = models.TimeField()
    detail_level_choices = [
        ('1sec', '1 Second'),
        ('1min', '1 Minute'),
        ('5min', '5 Minutes'),
        ('15min', '15 Minutes')
    ]
    detail_level = models.CharField(max_length=5, choices=detail_level_choices, default='1min')

    def __str__(self):
        return self.nom

class ParticipantExperiment(models.Model):
    experimentation = models.ForeignKey(Experimentation, on_delete=models.CASCADE)
    pilote = models.ForeignKey(Pilote, on_delete=models.CASCADE)
    average_heart_rate = models.FloatField(blank=True, null=True)
    max_heart_rate = models.FloatField(blank=True, null=True)
    min_heart_rate = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.pilote} - {self.experimentation}"
    
 
class HeartRateMeasurement(models.Model):
    participant_experiment = models.ForeignKey(ParticipantExperiment, on_delete=models.CASCADE, related_name='heart_rate_measurements')
    heure_mesure = models.TimeField()
    fréquence_cardiaque = models.IntegerField()

    def __str__(self):
        return f"Heart Rate Measurement for {self.participant_experiment}"
