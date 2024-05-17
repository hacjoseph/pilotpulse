from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Pilote
from pilotes.piloteSerializer import PiloteSerializer
from experimentations.models import Experimentation, ParticipantExperiment
from experimentations.experimentationSerializer import ExperimentationSerializer, ParticipantExperimentSerializer
from fitbit.views import authorize_fitbit
from django.http import FileResponse

class PiloteViewSet(ModelViewSet):
    queryset = Pilote.objects.all()
    serializer_class = PiloteSerializer
    
    def liste_pilotes(self, *args, **kwargs):
        """Cette méthode permet de recuperer la liste des pilotes

        Returns:
            Elle renvoie une reponse avec les donnéss séréalisées 
        """
        pilotes = self.get_queryset()
        serializer = self.get_serializer(pilotes, many=True)
        return Response({"data":serializer.data})

    @api_view(['POST'])
    def ajouter_compte_fitbit(request, pilote_id):
        if request.method == "POST":
            return authorize_fitbit(request, pilote_id)

    @api_view(['POST'])
    def ajouter_pilote(request):
        """Cette méthode permet de faire l'ajout d'un pilote

        Args:
            request une requete HTTP

        Returns:
            redirige l'utilisateur vers la page de connexion fitbit
        """
        
        serializer = PiloteSerializer(data=request.data)
        if serializer.is_valid():
            pilote = serializer.save()       
            return authorize_fitbit(request, pilote.id)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @api_view(['POST'])
    def modifier_pilote(request, pilote_id):
        """Cette méthode permet de modiffier les information d'un pilote

        Args:
            request : _Requete HTTP
            pilote_id : L'identifiant du pilote

        Returns:
             Elle renvoie une reponse avec les donnéés séréalisées 
        """
        pilote = get_object_or_404(Pilote, pk=pilote_id)
        
        serializer = PiloteSerializer(instance=pilote, data=request.data)
        if serializer.is_valid():
            pilote = serializer.save()
            
            return Response(serializer.data)
        return Response(serializer.errors, status=400 )


    @api_view(['DELETE'])
    def supprimer_pilote(request, pilote_id):
        """Cette méthode permet de supprimer un pilote

        Args:
            request : Requete HTTP
            pilote_id : Dl'identifiant du pilote

        """
        pilote = get_object_or_404(Pilote, pk=pilote_id)
        if request.method == 'DELETE':
            pilote.delete()
            return Response('Pilote supprimé avec succès')
        return Response('Erreur: Le pilote n\'a pas pu être supprimé ')

    @api_view(['GET'])
    def dashboard_pilote(request, pilote_id):
        """Cette méthode permet d'envoyer toutes les données nécessaires pour le dashboard d'un pilote."""
        
        # Récupération des détails du pilote
        pilote = get_object_or_404(Pilote, pk=pilote_id)
        pilote_serializer = PiloteSerializer(pilote)
        parser_classes = (MultiPartParser, FormParser)

        # Récupération des expérimentations du pilote
        participant_experiments = ParticipantExperiment.objects.filter(pilote=pilote)
        experimentations = Experimentation.objects.filter(participantexperiment__in=participant_experiments)
        experimentations_serializer = ExperimentationSerializer(experimentations, many=True)

        # Dictionnaire pour regrouper les mesures de fréquence cardiaque par expérimentation
        heart_rate_by_experimentation = {}
        
        # Parcourir tous les expérimentations du pilote
        for participant_experiment in participant_experiments:
            experiment_id = participant_experiment.experimentation.id
            
            if experiment_id not in heart_rate_by_experimentation:
                # Créer une nouvelle entrée pour cette expérimentation
                heart_rate_by_experimentation[experiment_id] = {
                    'labels': [],
                    'data': []
                }
            
            # Récupérer les mesures de fréquence cardiaque pour ce participant
            heart_rate_measurements = participant_experiment.heart_rate_measurements.all()
            
            # Ajouter les mesures de fréquence cardiaque à la liste de l'expérimentation correspondante
            for measurement in heart_rate_measurements:
                heart_rate_by_experimentation[experiment_id]['labels'].append(measurement.heure_mesure.strftime("%H:%M"))
                heart_rate_by_experimentation[experiment_id]['data'].append(measurement.fréquence_cardiaque)

        # Récupération des membres de chaque expérimentation
        experiment_members = {}
        for experimentation in experimentations:
            members = ParticipantExperiment.objects.filter(experimentation=experimentation.id).values_list('pilote__prenom', 'pilote__nom')
            experiment_members[experimentation.id] = list(members)  # Conversion en liste
        
        # Création du contexte de réponse
        response_data = {
            'pilote': pilote_serializer.data,
            'pilote_id': pilote.id,
            'experimentations': experimentations_serializer.data,
            'heart_rate_by_experimentation': heart_rate_by_experimentation,  # Correction ici
            'experiment_members': experiment_members,
        }
        
        return Response(response_data)

    
    @api_view(['DELETE'])
    def supprimer_utilisateur_fitbit(request, pilote_id):
        """Cette méthode permet de supprimer un compte fitbit d'un pilote

        Args:
            request : Requete HTTP
            pilote_id : Dl'identifiant du pilot
        """
        pilote = get_object_or_404(Pilote, pk=pilote_id)
        if request.method == 'DELETE':
            utilisateur_fitbit = pilote.fitbit_user
            if utilisateur_fitbit:
                utilisateur_fitbit.delete()
                return Response('Compte fitbit suppri avec succès')
        return Response('Erreur: Le pilote n\'a pas pu être supprimé ')