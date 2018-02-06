from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, TemplateView
from .models import Player

class PlayerList(ListView):
    queryset = Player.objects.all()
    context_object_name = 'players'

class Players(TemplateView):
    template_name = "players.html"
