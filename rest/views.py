from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer, PlayerSerializer
from top100.models import Player

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows user to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class Home(TemplateView):
    template_name = "home.html"
