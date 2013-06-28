from django.db import models
#from users.models import UserAccount

#This is to define Service


#define Service Category such as Cleaning, Guard etc
class Category(models.Model):

    """Service category class to define service category such as Cleaning, Guard, etc"""

    name = models.CharField(max_length=200)
    description = models.TextField()

    #return services of this Category
    def getServices(self):
        #return Service.objects.filter(category=self)
        return self.service_set.all()


#define Service such as Breakfast Cleaning, Dinner Prep, Guard A, etc
class Service(models.Model):

    """"ftta service class to define service such as Breakfast cleaning, Dinner, Prep, Guard A, etc"""

    category = models.ForeignKey(Category)
    name = models.CharField(max_length=1000)
    isActive = models.BooleanField()

    #every service have different workLoad, for example guard is much more intense than cleaning
    workLoad = models.IntegerField()


#define Service Period such as Pre-Training, FTTA regular week, etc
class Period(models.Model):

    """define Service Period such as Pre-Training, FTTA regular week, etc"""

    name = models.CharField(max_length=200)
    description = models.TextField()

    #which Service is on this Period
    service = models.ManyToManyField(Service)

    startDate = models.DateField('start date')
    endDate = models.DateField('end date')

    #return the services of this Period
    def getServices(self):
        return Service.objects.filter(period=self)

