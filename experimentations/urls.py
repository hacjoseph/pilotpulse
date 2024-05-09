from django.urls import path
from .views import ExperimentationViewSet

urlpatterns = [
    # path('', ExperimentationViewSet.liste_experimentations, name='liste_experimentations'),
    path('creer/', ExperimentationViewSet.creer_experimentation, name='creer_experimentation'),
    path('ajouter-pilote/<int:experimentation_id>/', ExperimentationViewSet.ajouter_pilote_experimentation, name='ajouter_pilote_experimentation'),
    path('modifier/<int:experimentation_id>/', ExperimentationViewSet.modifier_experimentation, name='modifier_experimentation'),
    path('dashboard/<int:experimentation_id>/', ExperimentationViewSet.dashboard_experimentation, name='dashboard_experimentation'),
    path('supprimer/<int:experimentation_id>/', ExperimentationViewSet.supprimer_experimentation, name='supprimer_experimentation'),
]

