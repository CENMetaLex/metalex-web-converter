from django.conf.urls.defaults import patterns
from metalex_web_converter.views import rdf_expression_data, xml_expression_data, no_xml_work_data, html_expression_data, rdf_work_data, html_work_data, negotiate, convert, redirect

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    ('^doc/BWB(\w\d+)(.*?)(\d\d\d\d-\d\d-\d\d)/data.xml$', xml_expression_data),
    ('^doc/BWB(\w\d+)(.*?)/data.xml$', no_xml_work_data),
    ('^doc/BWB(\w\d+)(.*?)(\d\d\d\d-\d\d-\d\d)/data.rdf$', rdf_expression_data),
    ('^doc/BWB(\w\d+)(.*?)/data.rdf$', rdf_work_data),
    ('^doc/BWB(\w\d+)(.*?)(\d\d\d\d-\d\d-\d\d)/data.html$', html_expression_data),
    ('^doc/BWB(\w\d+)(.*?)/data.html$', html_work_data),
    ('^doc/BWB(\w\d+)(.*?)$', negotiate),
    ('^id/BWB(\w\d+)(.*)$', redirect),
    ('^convert/(.+)$', convert)
)


