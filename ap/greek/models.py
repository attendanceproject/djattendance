from django.db import models

class Vocab(models.Model):
    
    PARSING_CODES = (
        ('N1D', 'Noun (1D)'),
        ('N2D', 'Noun (2D)'),
        ('N3D', 'Noun (3D)'),
        ('P', 'Participle'),
        ('Adj', 'Adjective'),
        ('V', 'Verb'),
        ('Vs', 'Verb (stem-changing)'),
        ('M', 'Misc'),
    )

    greek = models.CharField(max_length=200)
    english = models.CharField(max_length=500)
    chapter = models.IntegerField()
    parsing = models.CharField(max_length=5, choices=PARSING_CODES)

