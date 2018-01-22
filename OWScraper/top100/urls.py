from django.urls import path, include
from .views import PlayerList

urlpatterns = [
    path('', PlayerList.as_view()),
]
