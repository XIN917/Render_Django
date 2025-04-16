from rest_framework import serializers
from .models import Tribunal
from tfms.serializers import TFMReadSerializer  # Import the TFM serializer
from slots.serializers import SlotSerializer  # Import the Slot serializer
from users.serializers import UserSerializer  # Import the User serializer

class TribunalReadSerializer(serializers.ModelSerializer):
    tfm = TFMReadSerializer()  # Use the nested serializer for the TFM field
    slot = SlotSerializer()  # Use the nested serializer for the slots field
    president = UserSerializer()  # Use the nested serializer for the president field
    secretary = UserSerializer()  # Use the nested serializer for the secretary field
    vocals = UserSerializer(many=True)  # Use the nested serializer for the vocals field

    class Meta:
        model = Tribunal
        fields = '__all__'

class TribunalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunal
        fields = '__all__'

    def validate(self, data):
        president = data.get('president')
        secretary = data.get('secretary')
        vocals = data.get('vocals', [])

        # Validate president and secretary
        if president == secretary:
            raise serializers.ValidationError("President and secretary must be different.")
        if president.is_superuser or secretary.is_superuser:
            raise serializers.ValidationError("Superusers cannot be assigned as president or secretary.")

        # Validate vocals
        roles = {president, secretary}
        if roles & set(vocals):
            raise serializers.ValidationError("A judge cannot hold more than one role in a tribunal.")
        if len(vocals) < 1:
            raise serializers.ValidationError("At least one vocal is required.")
        if any(vocal.is_superuser for vocal in vocals):
            raise serializers.ValidationError("Superusers cannot be assigned as vocals.")

        return data