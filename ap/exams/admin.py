from django.contrib import admin
from exams.models import Exam, Makeup, Responses, Section, Session
from terms.models import Term

CURRENT_TERM = Term.current_term()


class ExamAdmin(admin.ModelAdmin):
  readonly_fields = ('total_score', 'section_count',)
  filter = ('training_class', 'term', 'category', 'is_open', 'is_graded_open')
  list_display = ('__unicode__', 'term', 'category', 'is_open', 'is_graded_open', 'duration', 'section_count')

  def get_queryset(self, request):
    qs = super(ExamAdmin, self).get_queryset(request)
    if CURRENT_TERM:
      return qs.filter(term=CURRENT_TERM)
    return qs


class ResponsesAdmin(admin.ModelAdmin):
  filter = ('session', 'section')
  list_display = ('pk', 'session', 'section', 'score', 'comments')

  def get_queryset(self, request):
    qs = super(ResponsesAdmin, self).get_queryset(request)
    if CURRENT_TERM:
      return qs.filter(session__exam__term=CURRENT_TERM)
    return qs


class ResponsesInline(admin.StackedInline):
  model = Responses
  extra = 0
  suit_classes = 'suit-tab suit-tab-responses'
  readonly_fields = ('section', )
  fields = ('section', 'score', ('responses', 'comments'), )


class SessionAdmin(admin.ModelAdmin):
  list_display = ('trainee', 'exam', 'is_submitted_online', 'is_graded', 'grade', 'time_started', 'time_finalized')
  fieldsets = (
      (None, {
          'classes': ('suit-tab', 'suit-tab-general',),
          'fields': ('trainee', 'exam', 'is_submitted_online', 'is_graded', 'time_finalized', 'grade')
      }),
  )
  suit_form_tabs = (('general', 'Session'),
                    ('responses', 'Reponses'))
  inlines = (ResponsesInline, )
  search_fields = ['trainee__firstname', 'trainee__lastname', 'exam__training_class__name', 'pk']  # to search up trainees

  def get_queryset(self, request):
    qs = super(SessionAdmin, self).get_queryset(request)
    if CURRENT_TERM:
      return qs.filter(exam__term=CURRENT_TERM)
    return qs


admin.site.register(Exam, ExamAdmin)
admin.site.register(Section)
admin.site.register(Session, SessionAdmin)
admin.site.register(Responses, ResponsesAdmin)
admin.site.register(Makeup)
