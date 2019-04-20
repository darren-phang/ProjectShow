from django import forms

from .models import CoursesHtml


class AdaptationForm(forms.ModelForm):
    class Meta:
        model = CoursesHtml
        fields = ("school", "contact", "html")
