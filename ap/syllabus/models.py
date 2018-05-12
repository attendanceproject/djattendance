from django.db import models
from classes.models import Class
from books.models import Book

from time import strftime

from django.contrib.postgres.fields import ArrayField

from django.core.urlresolvers import reverse, reverse_lazy

""" SYLLABUS models.py

This module catalogs all pertinent data associated with classes in the FTTA
for use in in other functions. For example, Data includes class name, date,
assignments, books, midterms, etc. Inputted data is organized into a
readable form for the entire term.

Data Models:
  - Syllabus:
    class_syllabus (ForeignKey: Class)
  - ClassSession:
    date
    topic
    book (ForeignKey: Book) - name(?), code
    assignment[]
    note
    exam (boolean, HIDDEN)
    syllabus (ForeignKey: Syllabus)
"""

class Syllabus (models.Model):

  # which class this syllabus belongs to
  class_syllabus = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)

  # whether assignment is read before or after class (== true)
  after = models.BooleanField(default=False)

  # def get_absolute_url(self):
  #   return reverse('self.class_syllabus.code')

  def get_absolute_url(self):
    return '%s/' % self.class_syllabus.term.code #reverse_lazy('detail-view', kwargs={'after': self.class_syllabus.code})

  def get_url(self):
    return '%s/' % self.class_syllabus.code

  def get_id(self):
    slug = self.id
    return slug

  class Meta:
    verbose_name_plural = 'syllabi'

  # @property
  # def _get_code(self):
  #   code= self.class_syllabus.code
  #   return code

  # codes = property(_get_code)

  def __unicode__(self):
    try:
      return (self.class_syllabus.name + " | " + self.class_syllabus.term.name)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  # code = Syllabus.class_syllabus.code

  # def get_code(self):
  #   code = self.class_syllabus.term.name
  #   return code


class ClassSession(models.Model):

  # date of the class
  date = models.DateField(verbose_name='session date')

  # topic; "exam";
  topic = models.CharField(max_length=200)

  # book name, code
  """ TO DO: Make this OPTIONAL. """
  """and make this multiple"""
  book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)

  # assignment info (pages; chapters; msgs; lessons; verses; exam: "FINAL, MIDTERM, ETC")
    # can list multiple assigments, e.g. memory verses
  assignment = ArrayField(models.CharField(max_length=100, blank=True), default=list())

  # exam (HIDDEN)
  exam = models.BooleanField(default=False)

  # the class syllabus this session refers to
  syllabus = models.ForeignKey(Syllabus, on_delete=models.SET_NULL, null=True)

  def __unicode__(self):
    try:
      return (self.syllabus.class_syllabus.name + " | "
          + self.syllabus.class_syllabus.term.name + " | " +
          self.date.strftime('%Y/%m/%d') + " | " + self.topic)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
