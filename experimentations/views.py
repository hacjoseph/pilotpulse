import logging
from statistics import mean
from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from experimentations.experimentationSerializer import ExperimentationSerializer, ParticipantExperimentSerializer, HeartRateMeasurementSerializer
from .models import Experimentation, HeartRateMeasurement, ParticipantExperiment
from pilotes.models import Pilote
from fitbit.views import authorize_fitbit,retrieve_heart_rate_data
import json

class ExperimentationViewSet(ModelViewSet):
    queryset = Experimentation.objects.all()
    serializer_class = ExperimentationSerializer

    def liste_experimentations(self, *args, **kwargs):
        """Cette methode permet de recuperer la liste des experimentations

        Returns:
            Elle retourn une reponse avec les donnees serealisees
        """
        experimentations = self.get_queryset()
        serializer = self.get_serializer(experimentations, many=True)
        return Response({"data":serializer.data})
    
    @api_view(['POST'])
    def creer_experimentation(request):
        """Cette methode permet de creer une experimentation

        Args:
            request: requete POST HTTP

        Returns:
            Elle retourne l'identifiant de l'experimentation cree
        """
        
        if request.method == 'POST':
            serializer = ExperimentationSerializer(data=request.data)
            if serializer.is_valid():
                experimentation = serializer.save()
                return Response({'experimentation_id': experimentation.id}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def ajouter_pilote_experimentation(request, experimentation_id):
        """Cette methode permet d'ajouter un pilote a une experimentation

        Args:
            request: requette http venant du front-end
            experimentation_id : l'identiifiant de l'exprimentation auquel on veut ajouter le pilote
        """
        experimentation = get_object_or_404(Experimentation, pk=experimentation_id)
        if request.method == 'POST':
            serializer = ParticipantExperimentSerializer(data=request.data)
            if serializer.is_valid():
                pilote_id = serializer.data['pilote']
                pilote = get_object_or_404(Pilote, pk=pilote_id)
                
                # verifier si le pilote appartient a l'experimentation
                if ParticipantExperiment.objects.filter(experimentation=experimentation, pilote=pilote).exists():
                    return Response("Le pilote appartient deja a l'experimentation")
                
                # Recuperation de l'identifiant du compte fitbit associe au pilote
                fitbit_user = pilote.fitbit_user
                
                # Verifier si un compte fitbit existe sinon rediriger l'utilisateur vers la page de connexion de fitbit
                if fitbit_user is None:
                    return authorize_fitbit(request, pilote_id=pilote.id)
                
                # Recuperation des donnees de la frequence cardiaque
                heart_rate_data = retrieve_heart_rate_data(request, experimentation, pilote)
                
                # sauvegarde des donnees dans la base de donnees
                ExperimentationViewSet.process_heart_rate_data(experimentation, pilote, heart_rate_data)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def process_heart_rate_data(experimentation, pilote, heart_rate_data):
        """Cette methode permet de sauvegarder la frequence cardiaque

        Args:
            experimentation
            pilote : pilote donc on a recuperer la frequence cadiaque
            heart_rate_data : les donnees de la frequence recuperee
        """
        participant_experiment = ParticipantExperiment.objects.create(experimentation=experimentation, pilote=pilote)
        
        # Ajoutez une vérification pour 'activities-heart-intraday'
        if 'activities-heart-intraday' in heart_rate_data:
                intraday_data = heart_rate_data['activities-heart-intraday']['dataset']
                if intraday_data:
                    for entry in intraday_data:
                        heart_rate_value = entry['value']
                        measurement_time = entry['time']
                        # Sauvegarde des données dans la table HeartRateMeasurement
                        heart_rate_mesurement = HeartRateMeasurement.objects.create(
                            participant_experiment=participant_experiment,
                            heure_mesure=measurement_time,
                            fréquence_cardiaque=heart_rate_value
                        )
                        heart_rate_mesurement.save()

            # Vérifiez avant d'utiliser 'max()' ou 'min()'
        if 'activities-heart' in heart_rate_data and intraday_data:
                participant_experiment.average_heart_rate = heart_rate_data['activities-heart'][0]['value']
                
                # Ajouter une vérification avant d'utiliser 'max()' et 'min()'
                max_value = max([entry['value'] for entry in intraday_data], default=None)
                min_value = min([entry['value'] for entry in intraday_data], default=None)

                if max_value is not None and min_value is not None:
                    participant_experiment.max_heart_rate = max_value
                    participant_experiment.min_heart_rate = min_value
                else:
                    participant_experiment.max_heart_rate = None
                    participant_experiment.min_heart_rate = None
                    
                participant_experiment.save()

            # Log avec vérification des valeurs
        if participant_experiment.average_heart_rate is not None:
                logging.debug("Fréquence cardiaque - Moyenne: %s, Max: %s, Min: %s", 
                            participant_experiment.average_heart_rate,
                            participant_experiment.max_heart_rate,
                            participant_experiment.min_heart_rate)
        else:
                logging.warning("Pas de fréquence cardiaque moyenne disponible.")

    @api_view(['POST'])
    def modifier_experimentation(request, experimentation_id):
        """ Cette methode permet de modifier les informations d'une experimetation

        Args:
            request : requette http venant du front-end
            experimentation_id : L'identifiant de l'experimentation

        Returns:
            _type_: _description_
        """
        experimentation = get_object_or_404(Experimentation, pk=experimentation_id)
        if request.method == 'POST':
            serializer = ExperimentationSerializer(instance=experimentation, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(serializer.errors, 'Informations de l\'experimentation non modufiés')

    @api_view(['DELETE'])
    def supprimer_experimentation(request, experimentation_id):
        """Cette methode permet de supprimer une experimetation

        Args:
            request :requette http venant du front-end
            experimentation_id : L'identifiant de l'experimentation

        Returns:
            _type_: _description_
        """
        experimentation = get_object_or_404(Experimentation, pk=experimentation_id)
        if request.method == 'DELETE':
            experimentation.delete()
            return Response('Expérimentation supprimé avec succès')
        return Response('Erreur: L\'expérimentation n\'a pas pu être supprimé ')

    @api_view(['GET'])
    def dashboard_experimentation(request, experimentation_id):
        """Cette méthode permet d'envoyer toutes les données nécessaires pour le tableau de bord de l'expérimentation"""

        experimentation = get_object_or_404(Experimentation, pk=experimentation_id)

        participant_experiments = ParticipantExperiment.objects.filter(experimentation=experimentation)

        # Dictionnaire pour les données de fréquence cardiaque par participant

        heart_rate_by_participant = {}


        # Variables pour stocker les valeurs globales min et max
        global_min = None
        global_max = None
        total_nbr_heart_rate = 0
        all_averages = []

        # Obtenir les données de fréquence cardiaque pour chaque participant

        for participant_experiment in participant_experiments:

            pilote = participant_experiment.pilote

            heart_rate_measurements = participant_experiment.heart_rate_measurements.all()

            # Initialiser les listes de labels et de données pour chaque participant

            labels = []

            heart_rate_data = []

            # Remplir les données de fréquence cardiaque

            for measurement in heart_rate_measurements:

                labels.append(measurement.heure_mesure.strftime("%H:%M"))

                heart_rate_data.append(measurement.fréquence_cardiaque)

            # Obtenir le min et le max des fréquences cardiaques pour chaque participant
            min_heart_rate = participant_experiment.min_heart_rate
            max_heart_rate = participant_experiment.max_heart_rate
            average_heart_rate = participant_experiment.average_heart_rate
            
        
            # Ajouter la moyenne à la liste des moyennes
            if average_heart_rate is not None:
                all_averages.append(average_heart_rate)

            # Mettre à jour les valeurs globales min et max
            if min_heart_rate is not None:
                if global_min is None or min_heart_rate < global_min:
                    global_min = min_heart_rate

            if max_heart_rate is not None:
                if global_max is None or max_heart_rate > global_max:
                    global_max = max_heart_rate

            # Calculer le nombre de valeurs de fréquence cardiaque dépassant 160
            high_mental_load_count = sum(1 for entry in heart_rate_data if entry > 100)
            participant_experiment.nbr_heart_rate = high_mental_load_count
            participant_experiment.save()

            # Ajouter les données de fréquence cardiaque au dictionnaire

            heart_rate_by_participant[pilote.id] = {
                'id': f"{pilote.id}",
                'nom': f"{pilote.prenom} {pilote.nom}",

                'role':f"{pilote.role}",
                'photo': f"/media/{pilote.photo}",
                'labels': labels,

                'data': heart_rate_data,
                'average_heart_rate': average_heart_rate,
                'min_heart_rate': min_heart_rate,
                'max_heart_rate': max_heart_rate,
                'nbr_heart_rate': high_mental_load_count,
            }

            total_nbr_heart_rate += high_mental_load_count


        # Calculer la moyenne globale des moyennes des participants
        global_average = mean(all_averages) if all_averages else None

        # Ajout des détails de l'expérimentation
        experimentation_details = {
            'nom': experimentation.nom,
            'date': experimentation.date.strftime("%d/%m/%Y"),
            'temps_debut': experimentation.temps_debut.strftime("%H:%M"),
            'temps_fin': experimentation.temps_fin.strftime("%H:%M"),
        }

        # Contexte de la réponse avec les données de fréquence cardiaque par participant et les min/max

        context = {

            'heart_rate_by_participant': heart_rate_by_participant,
            'global_heart_rate_range': {
                'min': global_min,
                'max': global_max,
            },
            'global_average_heart_rate': global_average,  
            'total_nbr_heart_rate': total_nbr_heart_rate,
            'experimentation_details': experimentation_details, 
        }

        return Response(context)