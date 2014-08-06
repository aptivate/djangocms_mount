from __future__ import unicode_literals, absolute_import

from datetime import date

from django.test import TestCase
from django.views.generic import ListView

from cms.plugin_pool import plugin_pool
from django_dynamic_fixture import G
from django_harness.fast_dispatch import FastDispatchMixin
from django_harness.html_parsing import HtmlParsingMixin
from django_harness.override_settings import override_settings
from django_harness.plugin_testing import PluginTestMixin

from djangocms_mount.cms_plugins import ViewMountPluginBase
from .models import Wossname, ExampleListPluginModel


class ExampleListView(ListView):
    model = Wossname
    template_name = "test_app/example_list_view.html"


class ExampleListPlugin(ViewMountPluginBase):
    model = ExampleListPluginModel
    view_class = ExampleListView
    render_template = ExampleListView.template_name

    def get_view_kwargs(self, request, context, instance, placeholder):
        return {'paginate_by': instance.limit}

plugin_pool.register_plugin(ExampleListPlugin)


class ExamplePluginTests(FastDispatchMixin, HtmlParsingMixin,
        PluginTestMixin, TestCase):

    plugin_model = ExampleListPluginModel
    plugin_class = ExampleListPlugin
    plugin_defaults = {'limit': 5}
    maxDiff = None

    def test_render_example_plugin_returns_correct_context(self):
        w1 = G(Wossname)
        w2 = G(Wossname)
        self.assertEqual([w1, w2], list(Wossname.objects.all()),
            "The other tests won't work unless exactly two Wossnames are returned")

        self.assertEqual([w1, w2], list(ExampleListView().get_queryset()),
            "The view must behave as expected, particularly around get_queryset()")

        context = self.prepare_plugin()
        self.assertEqual([w1, w2], list(context['object_list']),
            "The plugin should have placed the correct object list in the "
            "context returned to Django-CMS")

        request = self.get_fake_request(path='/fake')
        expected_response = ExampleListView.as_view()(request)
        expected_response.render()
        expected_html = expected_response.content

        actual_html = self.render_plugin()
        self.assertEqual(expected_html, actual_html,
            "The plugin should have returned the same HTML as the view does")

    def test_passing_parameters_from_plugin_to_view(self):
        self.instance.limit = 7
        context = self.prepare_plugin()
        self.assertIsNotNone(context['paginator'])
        self.assertEqual(7, context['paginator'].per_page)
