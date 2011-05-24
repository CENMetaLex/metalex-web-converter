'''
Created on 19 Apr 2011

@author: hoekstra
'''

from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE, RDF
from django.template.loader import get_template
from django.template import RequestContext
from rdflib import ConjunctiveGraph
from forms import QueryForm
import json

def search(request):
    if request.method == 'POST' :
        form = QueryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
#            date = form.cleaned_data['date']

            q = """PREFIX dcterms: <http://purl.org/dc/terms/> 
            PREFIX metalex: <http://www.metalex.eu/schema/1.0#> 
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT DISTINCT ?uri ?title ?date WHERE {
               ?uri a metalex:BibliographicExpression .
               ?uri dcterms:valid ?date .
               ?uri dcterms:title ?title .
               FILTER regex(str(?title),\""""+title+"""\")  
            } ORDER BY ?date"""
            
#            FILTER (?date <= \""""+str(date)+"""\"^^xsd:date)

            sparql = SPARQLWrapper("http://doc.metalex.eu:8000/sparql/")
            sparql.setQuery(q)
            
            sparql.setReturnFormat(JSON)
            sparql_results = sparql.query().convert()
            
            vars = sparql_results['head']['vars']
            
            results = []
            
            for row in sparql_results['results']['bindings'] :
                r = {}
                for var in vars :
                    v = row[var]
                    if v['type'] == 'uri' :
                        r[var] = v['value']
                    elif v['type'] == 'literal' :
                        r[var] = v['value']
                results.append(r)
            
            t = get_template('results.html')
            html = t.render(RequestContext(request, {'results': results,}))
            
            return HttpResponse(html)       

    else:
        form = QueryForm()
    
    t = get_template('search.html')
    html = t.render(RequestContext(request, {'form': form,}))
    return HttpResponse(html)


def net_expression_data(request, bwbid, path, version):
    if check_available(bwbid, path, version) :
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://doc.metalex.eu/files/{0}_{1}.net'.format(bwbid,version)
            
        return xml_response
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : version}))
        return HttpResponse(html)

def no_net_work_data(request, bwbid, path):
    t = get_template('no_net_work.html')
    html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path}))
    return HttpResponse(html) 

def xml_expression_data(request, bwbid, path, version):
    if check_available(bwbid, path, version) :
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://doc.metalex.eu/files/{0}_{1}_ml.xml'.format(bwbid,version)
            
        return xml_response
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : version}))
        return HttpResponse(html)

def no_xml_work_data(request, bwbid, path):
    t = get_template('no_xml_work.html')
    html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path}))
    return HttpResponse(html)    

def rdf_expression_data(request, bwbid, path, version):
    return describe(bwbid, path, version)

def rdf_work_data(request, bwbnr, path):
    return rdf_expression_data(request, bwbnr, path, '')

def turtle_expression_data(request, bwbid, path, version):
    return describe(bwbid, path, version, format='turtle')

def turtle_work_data(request, bwbnr, path):
    return turtle_expression_data(request, bwbnr, path, '')

def n3_expression_data(request, bwbid, path, version):
    return describe(bwbid, path, version, format='n3')

def n3_work_data(request, bwbnr, path):
    return turtle_expression_data(request, bwbnr, path, '')


def html_expression_data(request, bwbid, path, version):
    if check_available(bwbid, path, version) :
        html_response = HttpResponse('')
        html_response.status_code = '302'
        html_response['Location'] = 'http://www5.wiwiss.fu-berlin.de/marbles?uri=http://doc.metalex.eu/id/{0}{1}{2}'.format(bwbid,path,version)
            
        return html_response   
    else :
        t = get_template('not_converted.html')
        html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : version}))
        return HttpResponse(html)
#        return HttpResponse('<http://doc.metalex.eu/id/BWB{0}{1}{2}>'.format(bwbnr, path, version))

def html_work_data(request, bwbid, path):
    return html_expression_data(request, bwbid, path, '')


def negotiate(request, bwbid, path):
    req_accepted = request.accepted_types 
    
    # Registered handlers
    reg_handlers = {'application/xml': 'html', 'application/xhtml+xml': 'html', 'text/html': 'html',
                    'application/rdf+xml': 'rdf', 'text/rdf+n3': 'n3', 'application/x-turtle': 'n3', 
                    'text/xml': 'xml', 'text/plain': 'net'}

    uri_part = bwbid + path
    if not uri_part.endswith('/') :
        uri_part += '/'
    
    for mime in req_accepted :
        if mime in reg_handlers :
            redirect_suffix = reg_handlers[mime]
            response = HttpResponse('')
            response.status_code = '302'
            response['Location'] = 'http://doc.metalex.eu/doc/{0}data.{1}'.format(uri_part,redirect_suffix)
            
            return response
     
    t = get_template('message.html')
    html = t.render(RequestContext(request, { 'title': 'Unknown Accept Header', 'text' : 'Unfortunately we do not have content to serve for the accept header "{0}".'.format(request.META['HTTP_ACCEPT'])}))
    return HttpResponse(html)

def redirect_to_latest(request, bwbid, path):
    uri = '<http://doc.metalex.eu/id/{0}{1}>'.format(bwbid, path)
    
    q = """PREFIX dcterms: <http://purl.org/dc/terms/> 
PREFIX metalex: <http://www.metalex.eu/schema/1.0#> 
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?x ?date WHERE {
   ?x a metalex:BibliographicExpression .
   ?x metalex:realizes """ + uri + """ .
   ?x dcterms:valid ?date .
} ORDER BY ?date"""

    sparql = SPARQLWrapper("http://doc.metalex.eu:8000/sparql/")
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


def redirect(request, bwbid, path):    
    redir_response = HttpResponse('')
    redir_response.status_code = '303'
    redir_response['Location'] = 'http://doc.metalex.eu/doc/{0}{1}'.format(bwbid,path)
    
    return redir_response



def check_available(bwbid, path, version):
    uri = '<http://doc.metalex.eu/id/{0}{1}{2}>'.format(bwbid, path, version)
    q = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX metalex: <http://www.metalex.eu/schema/1.0#>\nASK { "+uri+" rdf:type ?x .}"
    
    sparql = SPARQLWrapper("http://doc.metalex.eu:8000/sparql/")
    sparql.setQuery(q)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results['boolean']

    
def describe(bwbid, path, version, format='rdfxml'):
    uri = '<http://doc.metalex.eu/id/{0}{1}{2}>'.format(bwbid, path, version)
    q = "DESCRIBE {0}".format(uri)
    
    sparql = SPARQLWrapper("http://doc.metalex.eu:8000/sparql/")
    sparql.setQuery(q)
    
    cg = sparql.queryAndConvert()    
    
    if format=='turtle' :
        response = HttpResponse(cg.serialize(format='turtle'))
        response['Content-Type'] = 'application/x-turtle'
    if format=='n3' :
        response = HttpResponse(cg.serialize(format='n3'))
        response['Content-Type'] = 'text/rdf+n3'
    elif format=='rdfxml' :
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


        



if __name__ == '__main__' :
    print check_available('R0015195','','')
    
    