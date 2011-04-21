'''
Created on 19 Apr 2011

@author: hoekstra
'''

from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from django.template.loader import get_template
from django.template import RequestContext

def xml_expression_data(request, bwbnr, path, version):
    if check_available(bwbnr, path, version) :
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://u017101.jur.uva.nl/files/BWB{0}_{1}_ml.xml'.format(bwbnr,version)
            
        return xml_response
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbnr, 'path' : path, 'version' : version}))
        return HttpResponse(html)

def no_xml_work_data(request, bwbnr, path):
    t = get_template('no_xml_work.html')
    html = t.render(RequestContext(request, {'bwb' : bwbnr, 'path' : path}))
    return HttpResponse(html)    

def rdf_expression_data(request, bwbnr, path, version):
    return describe(bwbnr, path, version)

def rdf_work_data(request, bwbnr, path):
    return rdf_expression_data(request, bwbnr, path, '')


def html_expression_data(request, bwbnr, path, version):
    if check_available(bwbnr, path, version) :
        html_response = HttpResponse('')
        html_response.status_code = '302'
        html_response['Location'] = 'http://doc.metalex.eu:3020/browse/list_resource?r=http://doc.metalex.eu/id/BWB{0}/{1}{2}'.format(bwbnr,path,version)
            
        return html_response   
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbnr, 'path' : path, 'version' : version}))
        return HttpResponse(html)
#        return HttpResponse('<http://doc.metalex.eu/id/BWB{0}{1}{2}>'.format(bwbnr, path, version))

def html_work_data(request, bwbnr, path):
    return html_expression_data(request, bwbnr, path, '')


def negotiate(request, bwbnr, path):
    accept_header = request.META['HTTP_ACCEPT']

    
    if accept_header.find('html') != -1:
        html_response = HttpResponse('')
        html_response.status_code = '302'
        html_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}{1}/data.html'.format(bwbnr,path)
        
        return html_response
    elif accept_header.startswith('application/rdf+xml' or accept_header.startswith('application/x-turtle') or accept_header.startswith('text/rdf+n3')) :        
        rdf_response = HttpResponse('')
        rdf_response.status_code = '302'
        rdf_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}{1}/data.rdf'.format(bwbnr,path)
        
        return rdf_response
    elif accept_header.startswith('application/xml') or accept_header.startswith('text/xml'):        
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}{1}/data.xml'.format(bwbnr,path)
        
        return xml_response
    else :
        return HttpResponse("Accept header is: {0}".format(accept_header))

def redirect(request, bwbnr, path):    
    redir_response = HttpResponse('')
    redir_response.status_code = '303'
    redir_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}{1}'.format(bwbnr,path)
    
    return redir_response


def check_available(bwbnr, path, version):
    uri = '<http://doc.metalex.eu/id/BWB{0}{1}{2}>'.format(bwbnr, path, version)
    q = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX metalex: <http://www.metalex.eu/schema/1.0#>\nASK { "+uri+" rdf:type ?x .}"
    
    sparql = SPARQLWrapper("http://doc.metalex.eu:3020/sparql/")
    sparql.setQuery(q)
    
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    for result in results :
        if result.endswith('"boolean":true}') :
            return True
        else :
            return False
    
def describe(bwbnr, path, version):
    uri = '<http://doc.metalex.eu/id/BWB{0}{1}{2}>'.format(bwbnr, path, version)
    q = "DESCRIBE {0}".format(uri)
    
    sparql = SPARQLWrapper("http://doc.metalex.eu:3020/sparql/")
    sparql.setQuery(q)
    
    response = HttpResponse(sparql.query())
    response['Content-Type'] = 'application/rdf+xml'
    
    return response
    
def convert(bwbid):
    pass

    
    