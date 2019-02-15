from django import forms

class FAQForm(forms.Form):
    question = forms.Textarea()
    answer = forms.Textarea()
    
    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
