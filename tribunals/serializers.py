# filepath: c:\UB\4th\TFG\backend\tribunals\serializers.py
from rest_framework import serializers
from .models import Tribunal
from tfms.serializers import TFMReadSerializer  # Import the TFM serializer
from slots.serializers import SlotSerializer  # Import the Slot serializer
from users.serializers import UserSerializer  # Import the User serializer

class TribunalSerializer(serializers.ModelSerializer):
    tfm = TFMReadSerializer()  # Use the nested serializer for the TFM field
    slot = SlotSerializer()  # Use the nested serializer for the slots field

    president = UserSerializer()  # Use the nested serializer for the president field
    secretary = UserSerializer()  # Use the nested serializer for the secretary field
    vocals = UserSerializer(many=True)  # Use the nested serializer for the vocals field

    class Meta:
        model = Tribunal
        fields = '__all__'