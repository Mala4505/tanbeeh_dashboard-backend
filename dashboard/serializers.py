
from rest_framework import serializers

class DashboardSerializer(serializers.Serializer):
    role = serializers.CharField()
    dashboardId = serializers.CharField()
    scope = serializers.DictField()
