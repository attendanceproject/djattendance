import urllib2
import json

from django.db import models


class OutlinePoint(models.Model):
  level = models.PositiveSmallIntegerField()
  string = models.CharField(max_length=20)

  def __unicode__(self):
    try:
      return self.string
    except AttributeError as e:
      return str(self.id) + ": " + str(e)


class Reference(models.Model):
  outline_point = models.ForeignKey(OutlinePoint, on_delete=models.SET_NULL, null=True)
  book = models.CharField(max_length=25)
  chapter = models.PositiveSmallIntegerField(null=True)
  verse = models.PositiveSmallIntegerField(null=True)
  end_chapter = models.PositiveSmallIntegerField(null=True)
  end_verse = models.PositiveSmallIntegerField(null=True)

  @property
  def string(self):
    if self.chapter is not None:
      s = self.book + ' ' + str(self.chapter)
      if self.verse is not None:
        s += ':' + str(self.verse)
      if self.end_chapter is not None:
        s += '-'
        if self.end_chapter == self.chapter:
          s += str(self.end_verse)
        else:
          s += str(self.end_chapter)
          if self.end_verse is not None:
            s += ':' + str(self.end_verse)
      return s
    else:
      return False


  def get_verses(self):
    '''
    Returns a dictionary {reference: verse} of a verse (or multiple consecutive verses)
    from a Reference object. Uses J.Tien's Recovery Version API.
    '''
    book_abbrev = self.book.strip('.').replace(' ', '')
    try:
      if self.end_chapter is None:
        response = urllib2.urlopen("http://rcvapi.herokuapp.com/v/%s/%d/%d" % (book_abbrev, self.chapter, self.verse,))
      else:
        response = urllib2.urlopen("http://rcvapi.herokuapp.com/vv/%s/%d/%d/%s/%d/%d" % (book_abbrev, self.chapter, self.verse, book_abbrev, self.end_chapter, self.end_verse,) )
      data = json.loads('[%s]' % response.read())
      verses = data[0]['verses']
      return verses
    except:
      return {}


  def __unicode__(self):
    try:
      return self.outline_point.string + str((self.book, self.chapter, self.verse, self.end_chapter, self.end_verse,))
    except AttributeError as e:
      return str(self.id) + ": " + str(e)
