from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=512)
    img = models.CharField(max_length=512)

class Comment(models.Model):
    comment = models.TextField()
    author = models.ForeignKey(Author, null=True, on_delete=models.SET_NULL)

class Position(models.Model):
    fen = models.CharField(max_length=71)
    cp = models.IntegerField(null=True)
    depth = models.IntegerField(null=True)
    comments = models.ManyToManyField(Comment)

class Player(models.Model):
    fideID = models.CharField(max_length=16)
    name = models.CharField(max_length=512)

class PlayerStats(models.Model):
    date = models.DateField()
    rating = models.IntegerField(null=True)
    title = models.CharField(max_length=3)
    player = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)

class Move(models.Model):
    curent_position = models.ForeignKey(Position, null=True, on_delete=models.SET_NULL)
    next_move = models.ForeignKey("self", null=True, on_delete=models.SET_NULL)
    san = models.CharField(max_length=10)

class Game(models.Model):
    date = models.DateField()
    white = models.ForeignKey(Player, related_name="white_player", null=True, on_delete=models.SET_NULL)
    black = models.ForeignKey(Player, related_name="black_player", null=True, on_delete=models.SET_NULL)
    moves = models.ManyToManyField(Move)



