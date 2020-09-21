from django.db import models
from django.urls import reverse

class Source(models.Model):
    name = models.CharField(max_length=40)
    url = models.CharField(max_length=100)
    keyword = models.CharField(max_length=50, default='Cardano')

    # def __str__(self):
    #     return self.name

    def get_absolute_url(self):
        return reverse("configure:create")

    # , kwargs = {'pk': self.pk}


# class Article(models.Model):
#     pub_date = models.DateField()
#     headline = models.CharField(max_length=200)
#     content = models.TextField()
#     reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.headline