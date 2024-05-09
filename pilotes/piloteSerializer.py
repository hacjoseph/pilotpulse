from rest_framework.serializers import ModelSerializer
from pilotes.models import Pilote

class PiloteSerializer(ModelSerializer):
    class Meta:
        model = Pilote
        fields = '__all__'