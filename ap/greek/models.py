from django.db import models

class Vocab(models.Model):
    
    PARSING_CODES = (
        ('1', 'Noun (1D)'),
        ('2', 'Noun (2D)'),
        ('3', 'Noun (3D)'),
        ('4', 'Participle'),
        ('5', 'Adjective'),
        ('6', 'Verb'),
        ('7', 'Verb (stem-changing)'),
        ('8', 'Misc'),
    )

    greek = models.CharField(max_length=200)
    english = models.CharField(max_length=500)
    chapter = models.IntegerField()
    parsing = models.CharField(max_length=5, choices=PARSING_CODES)

