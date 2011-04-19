from django.conf.urls.defaults import patterns, include, url
from metalex_web_converter.views import rdf_data, xml_data, html_page

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    ('^BWB(\w\d+)/(.*?)(\d\d\d\d-\d\d-\d\d)/data.xml$', xml_data),
    ('^BWB(\w\d+)/(.*?)(\d\d\d\d-\d\d-\d\d)/data.rdf$', rdf_data),
    ('^BWB(\w\d+)/(.*)/$', html_page)
)
