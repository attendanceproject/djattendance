from django.db import models
from accounts.models import Trainee

class Announcement(models.Model):

    ANNOUNCE_STATUS = (
        ('A', 'Approved'),
        ('P', 'Pending'),
        ('F', 'Fellowship'),
        ('D', 'Denied'),
        ('S', 'TA sister approved')
    )

    ANNOUNCE_TYPE = (
        ('CLASS', 'In-class'),
        ('SERVE', 'On the server')
    )

    status = models.CharField(max_length=1, choices=ANNOUNCE_STATUS, default='P')
    type = models.CharField(max_length=5, choices=ANNOUNCE_TYPE, default='CLASS')

    date_requested = models.DateTimeField(auto_now_add=True)
    trainee = models.ForeignKey(Trainee, null=True)
    comments = models.TextField()
    announcement = models.TextField()
    announcement_date = models.DateTimeField()
    announcement_end_date = models.DateTimeField(null=True) # this is required if it's on the server

    def __unicode__(self):
        return '<Announcement %s ...> by trainee %s' % (self.announcement[:10], self.trainee)

