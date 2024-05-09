from django import forms
from .models import Experimentation, ParticipantExperiment
from pilotes.models import Pilote

class ExperimentationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExperimentationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Experimentation
        fields = ['nom', 'date', 'temps_debut', 'temps_fin']
        labels = {
            'nom': 'Nom',
            'date': 'Date',
            'temps_debut': 'Temps de début',
            'temps_fin': 'Temps de fin',
        }
        widgets = {
            'nom': forms.TextInput(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'temps_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'temps_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ParticipantExperimentForm(forms.ModelForm):
    class Meta:
        model = ParticipantExperiment
        fields = ['id_pilote', 'heure_mesure', 'fréquence_cardiaque']
        labels = {
            'id_pilote': 'Pilote',
            'heure_mesure': 'Heure de mesure',
            'fréquence_cardiaque': 'Fréquence cardiaque'
        }
        widgets = {
            'id_pilote': forms.Select(),
            'heure_mesure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fréquence_cardiaque': forms.NumberInput(),
        }
