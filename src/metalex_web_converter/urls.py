from django.conf.urls.defaults import patterns
from metalex_web_converter.views import index, search, redirect_to_latest, expression_data, work_data, no_work_data, generic_data, negotiate, convert, redirect

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#urlpatterns = patterns('',
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.net$', net_expression_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.net$', no_net_work_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.xml$', xml_expression_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.xml$', no_xml_work_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.rdf$', rdf_expression_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.rdf$', rdf_work_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.n3$', n3_expression_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.n3$', n3_work_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.ttl$', turtle_expression_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.ttl$', turtle_work_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.html$', html_expression_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.html$', html_work_data),
#    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)$', negotiate),
#    ('^id/(?P<bwbid>BWB\w\d+)(?P<path>.*)/latest', redirect_to_latest),
#    ('^id/(?P<bwbid>BWB\w\d+)(?P<path>.*)$', redirect),
#    ('^convert/(.+)$', convert),
#    ('^search$', search),
#    ('^$', index)
#)


urlpatterns = patterns('',
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.(?P<format>(net|xml|rdf|n3|turtle|html))$', expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.(?P<format>(net|xml))$', no_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.(?P<format>(rdf|n3|turtle|html))', work_data),
    ('^doc/(?P<path>.*?)/data.(?P<format>(rdf|n3|turtle|html))$', generic_data),
    ('^doc/(?P<path>.*)$', negotiate),
    ('^id/(?P<bwbid>BWB\w\d+)(?P<path>.*)/latest', redirect_to_latest),
    ('^id/(?P<path>.*)$', redirect),
    ('^convert/(.+)$', convert),
    ('^search$', search),
    ('^$', index)
)