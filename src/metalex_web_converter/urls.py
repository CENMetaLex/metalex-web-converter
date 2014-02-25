# -*- coding: utf-8 -*-
'''
MetaLex Web Converter
=====================

@author: Rinke Hoekstra
@contact: hoekstra@uva.nl
@organization: Universiteit van Amsterdam
@version: 0.1
@status: beta
@website: http://doc.metalex.eu
@copyright: 2011, Rinke Hoekstra, Universiteit van Amsterdam
@deprecated: No longer used

@license: MetaLex Converter is free software, you can redistribute it and/or modify
it under the terms of GNU Affero General Public License
as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

You should have received a copy of the the GNU Affero
General Public License, along with MetaLex Converter. If not, see


Additional permission under the GNU Affero GPL version 3 section 7:

If you modify this Program, or any covered work, by linking or
combining it with other code, such other code is not for that reason
alone subject to any of the requirements of the GNU Affero GPL
version 3.

@summary: Django URL patterns for handling requests for MetaLex resources
'''

from django.conf.urls.defaults import patterns
from metalex_web_converter.views import index, search, redirect_to_latest, expression_data, work_data, no_work_data, generic_data, negotiate, convert, redirect, data, query

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
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)(?P<version>\d\d\d\d-\d\d-\d\d)/data.(?P<format>(net|xml|rdf|n3|ttl|html))$', expression_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.(?P<format>(net|xml))$', no_work_data),
    ('^doc/(?P<bwbid>BWB\w\d+)(?P<path>.*?)/data.(?P<format>(rdf|n3|ttl|html))', work_data),
    ('^doc/(?P<path>.*?)/data.(?P<format>(rdf|n3|ttl|html))$', generic_data),
    ('^doc/(?P<path>.*?)$', negotiate),
    ('^id/(?P<bwbid>BWB\w\d+)(?P<path>.*)/latest', redirect_to_latest),
    ('^(id|bwb)/(?P<path>.*)$', redirect),
    ('^convert/(.+)$', convert),
    ('^query$', query),
    ('^search$', search),
    ('^data$', data),
    ('^$', index)
)