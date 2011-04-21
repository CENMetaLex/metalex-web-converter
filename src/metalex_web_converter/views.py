'''
Created on 19 Apr 2011

@author: hoekstra
'''

from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from django.template.loader import get_template
from django.template import RequestContext

def xml_data(request, bwbnr, path, version):
    if check_available(bwbnr, path, version) :
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://u017101.jur.uva.nl/files/BWB{0}_{1}_ml.xml'.format(bwbnr,version)
            
        return xml_response
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbnr, 'path' : path, 'version' : version}))
        return HttpResponse(html)

def rdf_data(request, bwbnr, path, version):
    if check_available(bwbnr, path, version) :
        rdf_response = HttpResponse('')
        rdf_response.status_code = '302'
        rdf_response['Location'] = 'http://u017101.jur.uva.nl/files/BWB{0}_{1}.n3'.format(bwbnr,version)
            
        return rdf_response   
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbnr, 'path' : path, 'version' : version}))
        return HttpResponse(html)

def html_data(request, bwbnr, path, version):
    if check_available(bwbnr, path, version) :
        html_response = HttpResponse('')
        html_response.status_code = '302'
        html_response['Location'] = 'http://u017101.jur.uva.nl:3020/browse/list_resource?r=http://doc.metalex.eu/BWB{0}/{1}{2}'.format(bwbnr,path,version)
            
        return html_response   
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbnr, 'path' : path, 'version' : version}))
        return HttpResponse(html)


def negotiate(request, bwbnr, path, version):
    accept_header = request.META['HTTP_ACCEPT']
    
    if accept_header.find('html') != -1:
        html_response = HttpResponse('')
        html_response.status_code = '302'
        html_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}{2}/data.html'.format(bwbnr,path,version)
        
        return html_response
    elif accept_header.startswith('application/rdf+xml' or accept_header.startswith('application/x-turtle') or accept_header.startswith('text/rdf+n3')) :        
        rdf_response = HttpResponse('')
        rdf_response.status_code = '302'
        rdf_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}{2}/data.rdf'.format(bwbnr,path,version)
        
        return rdf_response
    elif accept_header.startswith('application/xml') or accept_header.startswith('text/xml'):        
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}{2}/data.xml'.format(bwbnr,path,version)
        
        return xml_response
    else :
        return HttpResponse("Accept header is: {0}".format(accept_header))

def redirect(request, bwbnr, path):    
    redir_response = HttpResponse('')
    redir_response.status_code = '303'
    redir_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}'.format(bwbnr,path)
    
    return redir_response


def check_available(bwbnr, path, version):
    uri = '<http://doc.metalex.eu/BWB{0}/{1}{2}>'.format(bwbnr, path, version)
    q = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX metalex: <http://www.metalex.eu/schema/1.0#>\nASK { "+uri+" rdf:type metalex:BibliographicExpression .}"
    
    sparql = SPARQLWrapper("http://u017101.jur.uva.nl:3020/sparql/")
    sparql.setQuery(q)
    
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    for result in results :
        if result.endswith('"boolean":true}') :
            return True
        else :
            return False
    
    
    
    
    