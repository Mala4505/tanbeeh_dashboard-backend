from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    hizb = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            'tr_number',
            'first_name',
            'last_name',
            'its_number',
            'class_name',
            'role',
            'hizb',
        ]
