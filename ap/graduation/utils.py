from aputils.trainee_utils import is_trainee
from graduation.models import Testimony, Consideration, Outline, Misc, Remembrance, GradAdmin, Website
from xb_application.models import XBApplication, XBAdmin
from terms.models import Term


def grad_forms(user):
  forms = []
  if is_trainee(user):

    admin, created = GradAdmin.objects.get_or_create(term=Term.current_term())
    models = [Testimony, Consideration, Outline, Remembrance, Website, Misc]
    for m in models:
      forms.append(m.objects.get_or_create(trainee=user, grad_admin=admin)[0])

    xb_admin, created = XBAdmin.objects.get_or_create(term=Term.current_term())
    forms.append(XBApplication.objects.get_or_create(trainee=user, xb_admin=xb_admin)[0])

    forms = filter(lambda f: (user.current_term == 4 and f.show_status != 'NO'), forms)

  return forms
