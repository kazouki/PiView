from django import forms
from .models import Source


class SourceForm(forms.ModelForm):

    class Meta:
        model = Source
        fields = '__all__'
        labels = {
            'name': '',
            'url': '',
            'keyword': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(size='8')
        self.fields['keyword'].widget.attrs.update(size='8')
        self.fields['url'].widget.attrs.update(size='8')







        # widgets = {
        #     'description': Textarea(attrs={'cols': 40, 'rows': 200})
        # }

    # def __init__(self, *args, **kwargs):
    #     super(ConfForm, self).__init__(*args, **kwargs)
    #
    #     self.fields['url'].help_text = 'fgdfg'
    #     self.fields['url'].label = 'dsfsdf'




    # def __init__(self, *args, **kwargs):
    #     super(ConfForm, self).__init__(*args, **kwargs)
    #     self.fields['url'].widget.attrs['placeholder'] = 'http://'
