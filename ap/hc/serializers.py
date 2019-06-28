from rest_framework.serializers import ModelSerializer

from .models import HCRecommendation

class HCRecommendationSerializer(ModelSerializer):

  class Meta(object):
    model = HCRecommendation
    fields = ['recommended_hc', 'choice', 'recommendation']
