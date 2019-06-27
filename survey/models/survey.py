# -*- coding: utf-8 -*-

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string


class Survey(models.Model):

    name = models.CharField(_("Name"), max_length=400)
    description = models.TextField(_("Description"))
    is_published = models.BooleanField(_("Users can see it and answer it"))
    need_logged_user = models.BooleanField(
        _("Only authenticated users can see it and answer it")
    )
    display_by_question = models.BooleanField(_("Display by question"))
    template = models.CharField(_("Template"), max_length=255, null=True, blank=True)

    slug = models.SlugField(max_length=8, blank=True, )  # blank we can migrate as this model doesn't already have this
    random_url = models.BooleanField(default=False, null=False, blank=False) # Decide if slug should be pk or random.

    class Meta(object):
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_save(self)  # call slug_save, listed below
        super(Survey, self).save(*args, **kwargs)

    def latest_answer_date(self):
        """ Return the latest answer date.

        Return None is there is no response. """
        min_ = None
        for response in self.responses.all():
            if min_ is None or min_ < response.updated:
                min_ = response.updated
        return min_

    def get_absolute_url(self):
        # if self.random_url == True:
        #     return reverse("survey-detail", kwargs={"slug": self.slug})
        # else:
        return reverse("survey-detail", kwargs={"id": self.pk})


def slug_save(obj):
    """ A function to generate an 8 character slug and see if it has been used."""
    if not obj.slug:  # if there isn't a slug
        obj.slug = get_random_string(8, '0123456789')  # create one
        slug_is_wrong = True
        while slug_is_wrong:  # keep checking until we have a valid slug
            slug_is_wrong = False
            other_objs_with_slug = type(obj).objects.filter(slug=obj.slug)
            if len(other_objs_with_slug) > 0:
                # if any other objects have current slug
                slug_is_wrong = True
            if slug_is_wrong:
                # create another slug and check it again
                obj.slug = get_random_string(5)
