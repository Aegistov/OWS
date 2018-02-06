from django.contrib.auth.models import User, Group
from top100.models import Player
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player 
        fields = ('player_tag', 'player_icon', 'char_one_name', 'char_one_image', 'char_two_name', 'char_two_image','char_three_name', 'char_three_image','char_four_name', 'char_four_image','char_five_name', 'char_five_image', 'elims_stat', 'heals_stat')
