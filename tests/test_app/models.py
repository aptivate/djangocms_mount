from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from extended_choices import Choices


class Wossname(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(ContentType)

    def __unicode__(self):
        return unicode(self.name)


class ExampleListPluginModel(CMSPlugin):
    limit = models.PositiveIntegerField(_('Number of events to show'),
            help_text=_('Limits the number of events that will be displayed'))

    title = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return _("%(title)s (%(limit)d)") % {
            'title': self.title,
            'limit': self.limit,
        }
