from django.shortcuts import render

from django.http import HttpResponse
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,
                                UpdateView)

from django.urls import reverse_lazy
from django.views.generic.edit import ModelFormMixin

from . import models
from . import forms



# class SourceView(TemplateView):
#     template_name = 'configure/source_list.html'

    # def get_context_data(self,**kwargs):
    #     context  = super().get_context_data(**kwargs)
    #     context['injectme'] = "Basic Injection!"
    #     return context

class SourceListView(ListView):
    template_name = 'configure/source_list.html'
    model = models.Source

    def get_queryset(self):
        return models.Source.objects.all()


class SourceDetailView(DetailView):
    model = models.Source
    template_name = 'configure/source_detail.html'


class SourceCreateView(CreateView, ModelFormMixin):
    form_class = forms.SourceForm
    model = models.Source

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        form = super(SourceCreateView, self).get_form(form_class)
        # form.fields['url'].widget.attrs['placeholder'] = 'URL'
        # form.fields['name'].widget.attrs['placeholder'] = 'Site name'
        # form.fields['description'].widget.attrs['placeholder'] = 'Description'

        form.fields['url'].widget.attrs['placeholder'] = 'URL'
        form.fields['name'].widget.attrs['placeholder'] = 'Source Name'
        form.fields['keyword'].widget.attrs['placeholder'] = 'Keyword'
        return form

    def get_context_data(self, **kwargs):
        context = super(SourceCreateView, self).get_context_data(**kwargs)
        context['created_objects'] = models.Source.objects.all()
        return context


class SourceDeleteView(DeleteView):
    model = models.Source
    success_url = reverse_lazy('configure:create')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class SourceUpdateView(UpdateView):
    form_class = forms.SourceForm
    model = models.Source


    # def get_form(self, form_class=None):
    #     if form_class is None:
    #         form_class = self.get_form_class()
    #
    #     form = super(SourceUpdateView, self).get_form(form_class)
    #     # form.fields['url'].widget.attrs['placeholder'] = 'URL'
    #     # form.fields['name'].widget.attrs['placeholder'] = 'Site name'
    #     # form.fields['description'].widget.attrs['placeholder'] = 'Description'
    #
    #     form.fields['url'].widget.attrs['placeholder'] = 'URL'
    #     form.fields['name'].widget.attrs['placeholder'] = 'Source Name'
    #     form.fields['description'].widget.attrs['placeholder'] = 'Description'
    #     return form


