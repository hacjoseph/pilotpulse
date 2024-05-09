from django.urls import path
from .views import PiloteViewSet


urlpatterns = [
    #path('', views.liste_pilotes, name='liste_pilotes'),
    path('add/', PiloteViewSet.ajouter_pilote, name='ajouter_pilote'),
    path('dashboard/<int:pilote_id>/', PiloteViewSet.dashboard_pilote, name='dashboard_pilote'),
    path('update/<int:pilote_id>/', PiloteViewSet.modifier_pilote, name='modifier_pilote'),
    path('delete/<int:pilote_id>/', PiloteViewSet.supprimer_pilote, name='supprimer_pilote'),
    path('fitbit/supprimer/<int:pilote_id>/', PiloteViewSet.supprimer_utilisateur_fitbit, name='supprimer_utilisateur_fitbit'),
    path('addfitbit/<int:pilote_id>/', PiloteViewSet.ajouter_compte_fitbit, name='ajouter_compte_fitbit'),

]

