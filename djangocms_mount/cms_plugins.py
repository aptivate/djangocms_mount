from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from mock import patch


class ViewMountPluginBase(CMSPluginBase):
    """
    You will need to configure:
    * model = YourPluginModel
    * view_class = YourListViewSubclass
    * render_template = template to use
    """

    def create_view(self, request, context, instance, placeholder):
        return self.view_class

    def get_view_kwargs(self, request, context, instance, placeholder):
        return {}

    # custom render method called by Django-CMS.
    def render(self, context, instance, placeholder):
        # Stash the plugin instance away so that get_paginate_by() can
        # retrieve it and get the limit value (page size) out.
        self.plugin_instance = instance

        # Prepare the view as though we'd called as_view()
        self.args = ()
        self.kwargs = {}

        # Call the View's get() method, which will return a context
        # instead of a Response, because we overrode create_response() to
        # do that.
        request = context['request']
        view = self.create_view(request, context, instance, placeholder)
        view_kwargs = self.get_view_kwargs(request, context, instance,
            placeholder)

        # Override render_to_response to return the context dict instead of an
        # HttpResponse. render() will incorporate this into the context dict
        # returned to DjangoCMS, which will render our template with it.
        with patch.object(view, 'render_to_response',
                lambda self, context: context) as patched_method:
            view_context = view.as_view(**view_kwargs)(request)

        # Add all the context variables set by ListView to the PluginContext
        context.update(view_context)

        # And return it for Django-CMS to render for us.
        return context
