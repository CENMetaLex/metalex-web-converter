from django.conf.urls.defaults import patterns
from metalex_web_converter.views import index, redirect_to_latest, turtle_expression_data, turtle_work_data, rdf_expression_data, xml_expression_data, no_xml_work_data, html_expression_data, rdf_work_data, html_work_data, net_expression_data, no_net_work_data, negotiate, convert, redirect

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.net$', net_expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.net$', no_net_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.xml$', xml_expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.xml$', no_xml_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.rdf$', rdf_expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.rdf$', rdf_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.n3$', turtle_expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.n3$', turtle_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.ttl$', turtle_expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.ttl$', turtle_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.html$', html_expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.html$', html_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)$', negotiate),
    ('^id/(?P<bwbid>BWB\w\d+)(?P<path>.*)/latest', redirect_to_latest),
    ('^id/(?P<bwbid>BWB\w\d+)(?P<path>.*)$', redirect),
    ('^convert/(.+)$', convert),
    ('^$', index)
)


