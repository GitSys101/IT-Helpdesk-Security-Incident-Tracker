from rest_framework import serializers
from .models import Ticket, TicketUpdate

class TicketSerializer(serializers.ModelSerializer):
    reporter_name = serializers.ReadOnlyField(source='reporter.username')
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.username')

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('reporter', 'created_at', 'updated_at', 'is_closed')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # If the user is a standard USER (not a technician/manager), mask these fields
        if request and request.user.is_authenticated and not request.user.is_technician:
            data.pop('priority', None)
            data.pop('assigned_to', None)
            data.pop('assigned_to_name', None)
            data.pop('is_closed', None)
            
        return data

class TicketUpdateSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = TicketUpdate
        fields = '__all__'
        read_only_fields = ('author', 'created_at')
