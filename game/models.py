from django.db import models


class Game(models.Model):
    turn = models.IntegerField(default=0)


class Gamer(models.Model):

    BLUE = "b"
    RED = "r"
    VALUE_CHOICES = ((BLUE, "Blue"), (RED, "Red"))

    team = models.CharField(max_length=1, choices=VALUE_CHOICES, null=True, blank=True)
    name = models.CharField(max_length=20)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class Card(models.Model):

    NOTHING = "n"
    CABLE = "c"
    BOMB = "b"
    VALUE_CHOICES = ((NOTHING, "Nothing"), (CABLE, "Cable"), (BOMB, "Bomb"))

    value = models.CharField(max_length=1, choices=VALUE_CHOICES, default=NOTHING)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    gamer = models.ForeignKey(Gamer, on_delete=models.SET_NULL, null=True, blank=True)


class Sky(models.Model):

    color = models.IntegerField()
    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return str(self.day) + '/' + str(self.month) + " ("+str(self.color) + ")"
