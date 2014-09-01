# DjangoCMS mount

Django-CMS adaptor to wrap Generic Class-Based Views as CMS Plugins

[![Build Status on Travis](https://travis-ci.org/aptivate/djangocms_mount.svg?branch=master)](https://travis-ci.org/aptivate/djangocms_mount)

## Purpose

Makes it easier to write plugins using standard generic views.

## Contents

The Github project contains the following files and directories:

* djangocms_mount: the app which you can add to `INSTALLED_APPS` in Django.
  * cms_plugins.py: A base class that you extend to create your plugin.
  * models.py: An empty models file to keep Django happy.

* tests: A test project which includes the mount app, some models and tests.
  * test_app: Is the customisation of the Events CMS app;
    * models.py: Example of model that could be used for your own plugin.
    * tests.py: Example/test for wrapping a view in a CMS plugin.

## Usage

### With DYE

To add `djangocms_mount` to your DYE project:

* add this line to `deploy/pip_packages.txt`:
    -e git+https://github.com/aptivate/djangocms_mount.git
* run `deploy/bootstrap.py`

### Manual Installation

If you're not using DYE, then install `djangocms_mount` in your global Python
environment or virtualenv:

    pip install djangocms_mount

Or if it's not available on PyPI, or you need a newer version:

    pip install -e git+https://github.com/aptivate/djangocms_mount.git

Of course you need [Django](https://www.djangoproject.com/)
(1.5 or higher) and
[Django-CMS](https://www.django-cms.org/en/) (2.4 or higher) in your
environment as well. They'll be installed automatically by Pip if you don't
have them already.

### Creating a CMS Plugin

You need to create a CMS plugin wrap a generic view. For example, consider this view:

    class ExampleListView(ListView):
        model = Wossname
        template_name = "test_app/example_list_view.html"

You'll need to create a model to store the configuration for each instance
of your plugin that the user adds in the CMS. For example, you could add this
to `models.py` in one of your apps:

    from django.db import models
    from cms.models.pluginmodel import CMSPlugin

    class ExampleListPluginModel(CMSPlugin):
        limit = models.PositiveIntegerField(_('Number of events to show'),
                help_text=_('Limits the number of events that will be displayed'))

        title = models.CharField(max_length=255, blank=True, null=True)

        def __unicode__(self):
            return _("%(title)s (%(limit)d)") % {
                'title': self.title,
                'limit': self.limit,
            }

The `__unicode__` method determines what you see in the Django-CMS backend
when you are looking at a page's placeholders and deciding which one to edit,
so it's useful to return a string that identifies this particular plugin
as much as possible.

Then you can wrap the View in a CMS plugin, for example in `cms_plugins.py` in
the same app:

    from cms.plugin_pool import plugin_pool
    from djangocms_mount.cms_plugins import ViewMountPluginBase

    class ExampleListPlugin(ViewMountPluginBase):
        model = ExampleListPluginModel
        view_class = ExampleListView
        render_template = ExampleListView.template_name
        cache = False  # Only enable caching when it makes sense for the plugin 

    plugin_pool.register_plugin(ExampleListPlugin)

Whenever the plugin is included in a page, it will render the template
specified by its `render_template` attribute. The example above uses the
same template as the generic View, but since that template probably
includes HTML <head> and <body> tags, etc, you probably want to use a
different template including just the HTML that you want to place into
the CMS page in the placeholder slot.

DjangoCMS caches plugin output by default, in version 3.0 you can disable this
with the `cache` attribute on the plugin class. You might want to do this if
your plugin returns dynamic content. Note that when `DEBUG=True` the plugin
cache is disabled so you might not see any problems until you try it in
production.

### Passing parameters to the view

Values stored in the plugin configuration can be passed to the view, for
example in the ExampleListPluginModel above the `limit` value allows users to
configure the number of items displayed on each page by the ListView paginator.

The `limit` value is accessible through the plugin model instance passed to
`get_view_kwargs`, you can use this to decide which kwargs to pass to the newly
constructed view. In our case passing `paginate_by` will set the page size for
the `ListView`.

    class ExampleListPlugin(ViewMountPluginBase):
        ...
        def get_view_kwargs(self, request, context, instance, placeholder):
            return {'paginate_by': instance.limit}

If you want to introduce new parameters, for example to filter the queryset
used by the view, you need to add them as properties of your View class:

    class ExampleListView(ListView):
        ...
        filter_by_name = None
        ...
        def get_queryset(self):
            return super(ExampleListView, self).get_queryset().filter(
                name=self.filter_by_name)

And now that they exist on the View, they'll be automatically assigned to
a newly created instance by `View.__init__`, if you pass them as keyword
arguments. So let's do that:

    class ExampleListPlugin(ViewMountPluginBase):
        ...
        def get_view_kwargs(self, request, context, instance, placeholder):
            return {
                'paginate_by': instance.limit,
                'filter_by_name': 'hello',
            }

You can also add them to the PluginModel, which allows users to configure
them differently on each instance of your plugin:

    class ExampleListPluginModel(CMSPlugin):
        ...
        filter_by_name = models.CharField(max_length=255)

    class ExampleListPlugin(ViewMountPluginBase):
        ...
        def get_view_kwargs(self, request, context, instance, placeholder):
            return {
                ...
                'filter_by_name': instance.filter_by_name,
            }

### Running the tests

You can clone the project from GitHub and run the tests manually with the
`tox` command, which installs all the test dependencies for you:

    tox

This will test with Python 2.6 and 2.7, so you'll need both installed. If
you just want to test one environment (which is faster and doesn't require
two Pythons to be installed) you can do this:

    tox -e py27-django16-cms3
