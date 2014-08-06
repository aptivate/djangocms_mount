import os

os.environ['DJANGO_SETTINGS_MODULE'] = \
    'tests.settings'

from setuptools import setup

setup(
    name='djangocms_mount',
    version='0.140804',
    author='http://www.aptivate.org/',
    author_email='support+djangocms_mount@aptivate.org',
    packages=['djangocms_mount'],
    include_package_data=True,
    url='https://github.com/aptivate/djangocms_mount',
    license='LICENSE',
    description='Django-CMS adaptor to wrap Generic Class-Based Views as CMS Plugins',
    #long_description=open('README.md').read(),
    setup_requires = [ "setuptools_git >= 0.3", ],
    install_requires=[
        "Django", # 1.5 or 1.6
        "django-cms", # 2.4 or 3.0
        "south >= 0.8.4",
        "mock >= 1.0.1",
    ],
    tests_require=[
    ],
    test_suite = "tests",
)
