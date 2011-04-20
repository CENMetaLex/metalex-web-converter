from django.conf.urls.defaults import patterns, include, url
from metalex_web_converter.views import rdf_data, xml_data, html_data, negotiate, redirect

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    ('^doc/BWB(\w\d+)/(.*?)(\d\d\d\d-\d\d-\d\d)/data.xml$', xml_data),
    ('^doc/BWB(\w\d+)/(.*?)(\d\d\d\d-\d\d-\d\d)/data.rdf$', rdf_data),
    ('^doc/BWB(\w\d+)/(.*?)(\d\d\d\d-\d\d-\d\d)/data.html$', html_data),
    ('^doc/BWB(\w\d+)/(.*)/$', negotiate)
    ('^id/BWB(\w\d+)/(.*)/$', redirect)
)
