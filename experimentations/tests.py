from django.test import TestCase, RequestFactory
from django.urls import reverse, reverse_lazy
from .models import Experimentation
from .views import ExperimentationViewSet
from datetime import datetime 
import pytz

class ExperimentationTestCase(TestCase):
    """Cette classe permet de faire les tests unitaire du modele experimentation

    Args:
        TestCase (_type_): Module de django qui permet de faire les test unitaires
    """
    def setUp(self) -> None:
        """Cette methode permet d'initialiser des variables qui seront utilisees dans toute la classe
        Tout ce qui se trouve dans cette methode est execute automatiquement lorqu'on lance un test.
        """
        self.factory = RequestFactory()
        
    def test_is_correct_instance(self):
        """Cette methode permet de verifier qu'une instance du model est bien creee
        """
        self.experimentation = Experimentation.objects.create(nom='experimentation1', date='2024-03-12', temps_debut= datetime(2024,3,12,11,20,0).replace(tzinfo=pytz.UTC), temps_fin= datetime(2024,3,12,11,30,0).replace(tzinfo=pytz.UTC))
        self.assertIsInstance(self.experimentation, Experimentation)
        
    def test_experimentation_list(self):
        """Cette methode permet de tester la recuperation de la liste des experimentations
        """
        
        #Creation de deux objets experimentation pour le test
        Experimentation.objects.create(
            nom='experimentation1', 
            date='2024-03-12', 
            temps_debut= '13:46', 
            temps_fin='13:49',
            detail_level = '5min'
        )
        
        Experimentation.objects.create(
            nom='experimentation2', 
            date='2024-02-02', 
            temps_debut= '13:46', 
            temps_fin='13:49',
            detail_level = '5min'
        )
        
        #Appel de la methode qui recupere la liste des pilotes
        response = self.client.get(reverse_lazy('liste_experimentations'))
        
        #Verifier que le code de la reponse HTTP est 200
        self.assertEqual(response.status_code, 200)

        #Verification des elements de la liste des experimentations
        experimentations = response.context['experimentations']
        self.assertEqual(len(experimentations), 2)
        self.assertEqual(experimentations[0].nom, "experimentation1")
        self.assertEqual(experimentations[1].nom, "experimentation2")


    def test_add_experimentation(self):
        """Cette methode permet de tester l'ajout d'une experimentation
        """ 
        
        #Simulation d'une requete POST
        data = {
            'nom':'experimentation1',
            'date':'2024-02-02', 
            'temps_debut': '13:46', 
            'temps_fin': '13:49',
            'detail_level' : '5min'
        }
        request = self.factory.post(reverse('creer_experimentation'), data)
        
        #Appel de la vue(methode) creer_experimentation avec la requete
        response = ExperimentationViewSet.creer_experimentation(request)
        
        #Verification de la redirection de la reponse vers la page d'ajout d'un pilote a un experimentation
        print(response)
        self.assertEqual(response.status_code, 200)
        experimentation_id = Experimentation.objects.get(nom='experimentation1').id
        # self.assertEqual(response.url, reverse('ajouter_pilote_experimentation', args=[experimentation_id]))
        
        #Verification de l'ajout de lexperimentation a la base de donnees
        self.assertTrue(Experimentation.objects.filter(nom = 'experimentation1').exists())

        
    def test_update_experimentation(self):
        
        # Creation de l'experimentation a modifier
        experimentation = Experimentation.objects.create(nom='experimentation1', date='2024-03-12',
        temps_debut= datetime(2024,3,12,11,20,0).replace(tzinfo=pytz.UTC), temps_fin= datetime(2024,3,12,11,30,0).replace(tzinfo=pytz.UTC))

        #Simulation d'une requete POST pour modifier le nom et la date d'une experimentation
        data = {
            'nom':'experimentation12',
            'date':'2024-02-02', 
            'temps_debut':datetime(2024,2,2,11,20,0).replace(tzinfo=pytz.UTC), 
            'temps_fin':datetime(2024,2,2,12,21,0).replace(tzinfo=pytz.UTC)
        }
        request = self.factory.post(reverse('modifier_pilote', args=[experimentation.id]), data)
        
        # Appel de la vue modifier experimentation
        response = ExperimentationViewSet.modifier_experimentation(request, experimentation.id)
        
        #Verification de la redirection vers la liste des experimentations apres modification
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('liste_experimentations'))

        #Verification de la modification de l'experimentation dans la base de donnees
        updated_experimentation = experimentation.objects.get(pk=experimentation.id)
        self.assertEqual(updated_experimentation.nom, 'Pilote5')
        self.assertEqual(updated_experimentation.date, '2024-02-02')
        
        
    def test_delete_experimentation(self):
        
        # Creation de deux experimentations
        experimentation1 = Experimentation.objects.create(nom='experimentation1', date='2023-03-12',
        temps_debut= datetime(2024,3,12,11,20,0).replace(tzinfo=pytz.UTC), temps_fin= datetime(2023,3,12,11,30,0).replace(tzinfo=pytz.UTC))
        experimentation2 = Experimentation.objects.create(nom='experimentation2', date='2024-03-12',
        temps_debut= datetime(2024,3,12,11,20,0).replace(tzinfo=pytz.UTC), temps_fin= datetime(2024,3,12,11,30,0).replace(tzinfo=pytz.UTC))

        #Creation d'une requete post pour supprimer l'experimentation1
        request = self.factory.post(reverse('supprimer_experimentation', args=[experimentation1.id]))
        
        #Appel de la vue supprimer_experimentation avec la requete
        response = ExperimentationViewSet.supprimer_experimentation(request, experimentation1.id)
        
        #Verification de la suppression de l'experimentation1
        experimentation_deleted = Experimentation.objects.filter(pk=experimentation1.id).exists()
        self.assertFalse(experimentation_deleted)

        #Verification de redirection vers la liste des experimentations
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('liste_experimentations'))
        
        #Verification du nombre d'experimentations apres la suppression de l'experimentation1. voir c'est egal a 1
        response = self.client.get(reverse('liste_experimentations'))
        experimentations = response.context['experimentations']
        self.assertEqual(len(experimentations), 1)