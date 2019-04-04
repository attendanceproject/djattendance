from django.views.generic import TemplateView

class MessagingView(TemplateView):
  template_name = "messaging/inbox.html"

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    ctx = super(MessagingView, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Team Statistics'
    return ctx
