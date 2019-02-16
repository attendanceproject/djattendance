

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

# unsure of import ValidationError


class FAQ(models.Model):    
	
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    isAnswered = models.BooleanField(default=False)
    '''
    def __unicode__(self):
	    try:
	      return "%s %s" % (self.question, self.answer)
	    except AttributeError as e:
	      return str(self.id) + ": " + str(e)
	'''

'''
class Scores(models.Model):
	house_id = # foreign key to houses from 'manage inspectable houses'
	date = models.DateTimeField(default=datetime.now, blank=True)
	ric = # a list of trainees in the house? Where to get?
	inspectors = # list of all inspectors. Be able to select 2.
	score = models.DecimalField(max_digits=1, decimal_places=2)
	notes = models.TextField(blank=True)
	uninspectable = models.BooleanField(default=False)


	House ID - Dropdown of all current houses
	Date 	- Date Selection (current date default)
	RIC			- Textbox dropdown list of all trainees
	Inspectors	- Textbox with dropdown list of all inspectors. Be able to select 2 inspectors
	Score		- Textbox
	Notes		- Textbox
	Uninspectable	- Checkbox. If checked, dropdown list shows up with options:
				- sick trainee
				- inspection error
				- office says it is uninspectable
				- other (with textbook)
'''

class Inspectors(models.Model):
	trainee = models.ForeignKey('accounts.Trainee', on_delete=models.SET_NULL, null=True)
	last_name = models.CharField(max_length=200)
	first_name = models.CharField(max_length=200)
	term = models.IntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(4)],
		default=1,
		null=False
		)
	prefect_number = models.IntegerField(
		validators= [MaxValueValidator(999)],
		default=0,
		null=False
		)
	def __str__(self):
		return '%s' % (self.last_name)#(self.first_name, self.last_name)

class InspectableHouses(models.Model):
	residence = models.ForeignKey('houses.House', null=True)
	residence_type = models.CharField(max_length=10)
	uninspectable = models.BooleanField(default=False)
	def __str__(self):
		return '%s' % (self.residence)


'''
class Listing(models.Model):
	realtor = models.ForeignKey(Realtor, on_delete=models.DO_NOTHING)
	title = models.CharField(max_length=200)
	address = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	zipcode = models.CharField(max_length=20)
	description = models.TextField(blank=True) # this means it is optional.
	price = models.IntegerField()
	bedrooms = models.IntegerField()
	bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
	garage = models.IntegerField(default=0)
	sq_ft = models.IntegerField()
	lot_size = models.DecimalField(max_digits=5, decimal_places=1)
	photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/') # define where it gets uploaded to. 
	photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
	photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
	photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
	photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
	photo_5 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
	photo_6 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
	is_published = models.BooleanField(default=True)
	list_date = models.DateTimeField(default=datetime.now, blank=True)
	# we need a main field to be displayed.
	def __str__(self):
		return self.title
'''