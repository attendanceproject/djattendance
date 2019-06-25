
from datetime import date, datetime, timedelta

from accounts.models import Trainee
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

# unsure of import ValidationError

class HouseInspectionFaq(models.Model):
	TYPE_APPROVAL_STATUS_CHOICES = (
    	('A', 'Approved'),
    	('An', 'Answered'),
    	('U', 'Unanswered'),
    	('D', 'Denied')
    )

	question = models.TextField(null=True, blank=True)
	answer = models.TextField(null=True, blank=True)
	status = models.CharField(choices=TYPE_APPROVAL_STATUS_CHOICES, max_length=2, default='U')
	trainee = models.ForeignKey(Trainee, blank=True, null=True, on_delete=models.SET_NULL)
	date_assigned = models.DateTimeField(auto_now_add=True)
	comment = models.TextField(blank=True, null=True)

	def get_absolute_url(self):
		return reverse('house_inspection:house_inspection_faq-detail', kwargs={'pk': self.id})

	def get_category(self):
		return

	def get_date_created(self):
		return self.date_assigned

	def get_status(self):
		return self.get_status_display()

	def get_question(self):
		return self.question

	def get_answer(self):
		return self.answer

	def get_comment(self):
		return self.comment

	@property
	def requester_name(self):
		if self.trainee:
		  return self.trainee.full_name
		return "Guest"

	def get_trainee_requester(self):
	    return self.trainee

	@staticmethod
	def get_create_url():
		return reverse('house_inspection:faq-create')

	def get_update_url(self):
		return reverse('house_inspection:faq-update', kwargs={'pk': self.id})

	def get_absolute_url(self):
		return reverse('house_inspection:house_inspection_faq-detail', kwargs={'pk': self.id})

	def get_delete_url(self):
		return reverse('house_inspection:faq-delete', kwargs={'pk': self.id})

	def get_answer_url(self):
		return reverse('house_inspection:inspector-answer', kwargs={'pk': self.id})

	@staticmethod
	def get_detail_template():
		return 'house_inspection/faq_description.html'

	@staticmethod
	def get_table_template():
		return 'house_inspection/faq_detail_table.html'

	@staticmethod
	def get_ta_button_template():
		return 'house_inspection/ta_buttons.html'

	@staticmethod
	def get_button_template():
		return 'house_inspection/buttons.html'

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
	residence = models.ForeignKey('houses.House', null=True, on_delete=models.CASCADE)
	residence_type = models.CharField(max_length=10)
	uninspectable = models.BooleanField(default=False)
	def __str__(self):
		return '%s' % (self.residence)
