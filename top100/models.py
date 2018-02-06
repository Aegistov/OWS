from django.db import models

# Create your models here.
class Player(models.Model):
    player_tag = models.CharField(max_length=120)
    player_icon = models.CharField(max_length=120)
    char_one_name = models.CharField(max_length=50)
    char_one_image = models.CharField(max_length=120)
    char_two_name = models.CharField(max_length=50)
    char_two_image = models.CharField(max_length=120)
    char_three_name = models.CharField(max_length=50)
    char_three_image = models.CharField(max_length=120)
    char_three_name = models.CharField(max_length=50)
    char_three_image = models.CharField(max_length=120)
    char_four_name = models.CharField(max_length=50)
    char_four_image = models.CharField(max_length=120)
    char_five_name = models.CharField(max_length=50)
    char_five_image = models.CharField(max_length=120)
    elims_stat = models.CharField(max_length=50)
    heals_stat = models.CharField(max_length=50)

