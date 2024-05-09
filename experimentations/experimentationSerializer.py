from rest_framework.serializers import ModelSerializer
from experimentations.models import Experimentation, ParticipantExperiment, HeartRateMeasurement

class ExperimentationSerializer(ModelSerializer):
    class Meta:
        model = Experimentation
        fields = '__all__'
        
class ParticipantExperimentSerializer(ModelSerializer):
    class Meta:
        model = ParticipantExperiment
        fields = '__all__'
        
        
class HeartRateMeasurementSerializer(ModelSerializer):
    class Meta:
        model = HeartRateMeasurement
        fields = '__all__'