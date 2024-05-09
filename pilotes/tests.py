from django.test import TestCase, RequestFactory
from django.urls import reverse, reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Pilote
from pilotes.views import PiloteViewSet

class PiloteTestCase(TestCase):
    def setUp(self) -> None:
        # 'pilote.jpeg' = SimpleUploadedFile("/pilote_photos/pilote.jpeg", b"file_content", content_type="image/jpeg")
        self.factory = RequestFactory()
        
        
    def test_is_correct_instance(self):
        self.pilote = Pilote.objects.create(prenom = 'Pilote1', nom='Pilote1', role = 'Capitaine', age=40, experience=15, photo='pilote.jpeg', sexe='M')
        self.assertIsInstance(self.pilote, Pilote)
        
    def test_pilote_list(self):
        
        #Creation de deux objets pilote pour le test
        pilote = Pilote.objects.create(prenom = 'Pilote1', nom='Pilote1', role = 'Capitaine', age=40, experience=15, photo='pilote.jpeg', sexe='M')
        # Pilote.objects.create(prenom = 'Pilote2', nom='Pilote2', role = 'Commandante', age=36, experience=16, photo='pilote.jpeg', sexe='F')
        
        #Appel de la methode qui recupere la liste des pilotes
        response = self.client.get(reverse_lazy('pilotes-list'))
        
        #Nous verifions que la reponse du status code HTTP est bien 200
        self.assertEqual(response.status_code, 200)
        
        # Nous verifions que les valeurs retournnees sont bien celles attendues
        expected = [
            {
                'id': pilote.pk,
                'prenom' : pilote.prenom,
                'nom' : pilote.nom, 
                'role' : pilote.role, 
                'age' : pilote.age, 
                'experience':pilote.experience, 
                'photo':pilote.photo, 
                'sexe' : pilote.sexe,
                
            },
        ]
        
        self.assertEqual(expected, response.json())
        
        
    def test_add_pilote(self):
        
        #Simulation d'une requete POST
        data = {
            'prenom' : 'Pilote1', 
            'nom' : 'Pilote', 
            'role' : 'Capitaine', 
            'age' : 40, 'experience':15, 
            'photo':'pilote.jpeg', 
            'sexe' : 'M', 
            'redirect_to':'http://localhost:3000/pilots/'
        }
        request = self.factory.post(reverse_lazy('ajouter_pilote'), data)
        
        #Appel de la vue ajouter_pilote avec la requete
        response = PiloteViewSet.ajouter_pilote(request)
        
        #Verification de l'ajout du pilote a la base de donnees
        self.assertTrue(Pilote.objects.filter(nom = 'Pilote').exists())
        
        
    def test_update_pilote(self):
        
        #Creation du pilote a modifier
        pilote = Pilote.objects.create(prenom = 'Pilote1', nom='Pilote', role = 'Capitaine', age=40, experience=15, photo='pilote.jpeg', sexe='M') 
        
        #Simulation d'une requete POST pour modifier le prenom, l'age et le sexe du pilote
        data = {'prenom' : 'Pilote5', 'nom' : 'Pilote', 'role' : 'Capitaine', 'age' : 32, 'experience':15, 'photo':'pilote.jpeg', 'sexe' : 'F'}
        request = self.factory.post(reverse_lazy('modifier_pilote', args=[pilote.id]), data)
        
        #Appel de la vue modifier_pilote
        response = PiloteViewSet.modifier_pilote(request, pilote.id)

        #Verification de la modification du pilote dans la base de donnees
        updated_pilote = Pilote.objects.get(pk=pilote.id)
        self.assertEqual(updated_pilote.prenom, 'Pilote5')
        self.assertEqual(updated_pilote.age, 32)
        self.assertEqual(updated_pilote.sexe, 'F')


    def test_delete_pilote(self):
        
        #Creation de deux pilotes
        pilote1 = Pilote.objects.create(prenom = 'Pilote1', nom='Pilote1', role = 'Capitaine', age=40, experience=9, photo='pilote.jpeg', sexe='M')
        pilote2 = Pilote.objects.create(prenom = 'Pilote2', nom='Pilote2', role = 'Commandant', age=42, experience=15, photo='pilote.jpeg', sexe='M')
        
        #Creation d'une requete post pour supprimer le pilote1
        request = self.factory.post(reverse('supprimer_pilote', args=[pilote1.id]))
        
        #Appel de la vue supprimer_pilote avec la requete
        response = PiloteViewSet.supprimer_pilote(request, pilote1.id)
        
        #Verification de la suppression du pilote
        pilote_deleted = Pilote.objects.filter(pk=pilote1.id).exists()
        self.assertTrue(pilote_deleted)
        
        #Verification du nombre de pilotes apres la suppression du pilote1 voir est egal a 1
        # response = self.client.get(reverse_lazy('liste_pilotes'))
        # pilotes = response.context['pilotes']
        # self.assertEqual(len(pilotes), 1)
        