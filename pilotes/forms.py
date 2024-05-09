from django import forms
from .models import Pilote

class PiloteForm(forms.ModelForm):
    class Meta:
        model = Pilote
        fields = ['prenom', 'nom', 'role', 'age', 'sexe']
        labels = {
            'prenom': 'Prénom',
            'nom': 'Nom',
            'role': 'Rôle',
            'age': 'Âge',
            'experience': 'Expérience',
            'sexe': 'Sexe',
            'photo': 'Photo',
        }
        widgets = {
            'prenom': forms.TextInput(),
            'nom': forms.TextInput(),
            'role': forms.TextInput(),
            'age': forms.NumberInput(),
            'experience': forms.TextInput(),
            'sexe': forms.TextInput(),
            'photo': forms.URLInput(),
        }
