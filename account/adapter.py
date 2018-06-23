from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomizeAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        msg.send(fail_silently=True)
