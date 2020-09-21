from django import forms


class requestForm(forms.Form):
    name = forms.CharField(label="Url ", max_length=264)
    topic = forms.CharField(label="Topic ", max_length=264)

