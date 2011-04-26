'''
Created on 19 Apr 2011

@author: hoekstra
'''

from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from django.template.loader import get_template
from django.template import RequestContext
import json

def xml_expression_data(request, bwbnr, path, version):
    if check_available(bwbnr, path, version) :
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://doc.metalex.eu/files/BWB{0}_{1}_ml.xml'.format(bwbnr,version)
            
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
        html_response['Location'] = 'http://doc.metalex.eu:3020/browse/list_resource?r=http://doc.metalex.eu/id/BWB{0}{1}{2}'.format(bwbnr,path,version)
            
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

    uri_part = bwbnr + path
    if not uri_part.endswith('/') :
        uri_part += '/'
    
    if accept_header.find('html') != -1:
        html_response = HttpResponse('')
        html_response.status_code = '302'
        html_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}data.html'.format(uri_part)
        
        return html_response
    elif accept_header.startswith('application/rdf+xml' or accept_header.startswith('application/x-turtle') or accept_header.startswith('text/rdf+n3')) :        
        rdf_response = HttpResponse('')
        rdf_response.status_code = '302'
        rdf_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}data.rdf'.format(uri_part)
        
        return rdf_response
    elif accept_header.startswith('application/xml') or accept_header.startswith('text/xml'):        
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}data.xml'.format(uri_part)
        
        return xml_response
    else :
        t = get_template('message.html')
        html = t.render(RequestContext(request, { 'title': 'Unknown Accept Header', 'text' : 'Unfortunately we do not have content to serve for the accept header "{0}".'.format(accept_header)}))
        return HttpResponse(html)

def redirect_to_latest(request, bwbnr, path):
    uri = '<http://doc.metalex.eu/id/BWB{0}{1}>'.format(bwbnr, path)
    
    q = """PREFIX dcterms: <http://purl.org/dc/terms/> 
PREFIX metalex: <http://www.metalex.eu/schema/1.0#> 
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?x ?date WHERE {
   ?x a metalex:BibliographicExpression .
   ?x metalex:realizes """ + uri + """ .
   ?x dcterms:valid ?date .
} ORDER BY ?date"""

    sparql = SPARQLWrapper("http://doc.metalex.eu:3020/sparql/")
    sparql.setQuery(q)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert().read()
    
    result_dict = json.loads(results)
    
    try :
        result = result_dict["results"]["bindings"][0]["x"]["value"] 
        
        redir_response = HttpResponse('')
        redir_response.status_code = '303'
        redir_response['Location'] = result
        
        return redir_response
    except :
        t = get_template('message.html')
        html = t.render(RequestContext(request, { 'title': 'Oops', 'text' : 'No expression found for this work URI.'}))
        return HttpResponse(html)


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
    
def convert(request, bwbid):
    t = get_template('message.html')
    html = t.render(RequestContext(request, { 'title': 'Not Implemented', 'text' : 'Unfortunately this functionality has not been implemented yet. See <a href="/">here</a> for more information.'}))
    return HttpResponse(html)

def index(request):
    t = get_template('index.html')
    html = t.render(RequestContext(request, {}))
    return HttpResponse(html)

    
    