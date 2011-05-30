'''
Created on 19 Apr 2011

@author: hoekstra
'''

from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from django.template.loader import get_template
from django.template import RequestContext
from rdflib import Namespace
from forms import QueryForm
import json

def search(request):
    if request.method == 'POST' :
        form = QueryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            date = form.cleaned_data['date']

            q = """PREFIX dcterms: <http://purl.org/dc/terms/> 
            PREFIX metalex: <http://www.metalex.eu/schema/1.0#> 
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            
            SELECT DISTINCT ?uri ?title ?date ?xml WHERE {
               ?uri a metalex:BibliographicExpression .
               ?uri dcterms:valid ?date .
               ?uri dcterms:title ?title .
               ?uri foaf:page ?xml .
               FILTER (regex(str(?title),\""""+title+"""\", "i") && (xsd:dateTime(?date) <= xsd:dateTime(\""""+str(date)+"""\")))
            } ORDER BY ?date"""
            
            

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
                        if var == 'xml' :
                            r['rdf'] = r[var].replace('data.xml','data.rdf')
                            r['n3'] = r[var].replace('data.xml','data.n3')
                            r['net'] = r[var].replace('data.xml','data.net')
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


def generic_data(request, path, format):
    return describe(path, format)

def expression_data(request, bwbid, path, version, format):
    if (format == 'net' or format == 'xml') :
        if check_available(bwbid, path, version) :
            response = HttpResponse('')
            response.status_code = '302'
            response['Location'] = 'http://doc.metalex.eu/files/{0}_{1}.{2}'.format(bwbid,version,format)
                
            return response
        else :
            t = get_template('not_converted.html')
            html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : version}))
            return HttpResponse(html)
    elif (format == 'rdf' or format == 'n3' or format == 'ttl') :
        return describe(bwbid + path + version, format)
    elif (format == 'html') :
        if check_available(bwbid, path, version) :
            html_response = HttpResponse('')
            html_response.status_code = '302'
            html_response['Location'] = 'http://www5.wiwiss.fu-berlin.de/marbles?uri=http://doc.metalex.eu/id/{0}{1}{2}'.format(bwbid,path,version)
                
            return html_response   
        else :
            t = get_template('not_converted.html')
            html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : version}))
            return HttpResponse(html)        

def no_work_data(request, bwbid, path, format):
    t = get_template('no_work.html')
    html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'format' : format}))
    return HttpResponse(html) 

def work_data(request, bwbid, path, format):
    if (format == 'rdf' or format == 'n3' or format == 'ttl') :
        return describe(bwbid + path, format)
    elif (format == 'html') :
        if check_available(bwbid, path, '') :
            html_response = HttpResponse('')
            html_response.status_code = '302'
            html_response['Location'] = 'http://www5.wiwiss.fu-berlin.de/marbles?uri=http://doc.metalex.eu/id/{0}{1}'.format(bwbid,path)
                
            return html_response   
        else :
            t = get_template('not_converted.html')
            html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : ''}))
            return HttpResponse(html)


def negotiate(request, path):
    req_accepted = request.accepted_types 
    
    # Registered handlers
    reg_handlers = {'application/xml': 'html', 'application/xhtml+xml': 'html', 'text/html': 'html',
                    'application/rdf+xml': 'rdf', 'text/rdf+n3': 'n3', 'application/x-turtle': 'n3', 
                    'text/xml': 'xml', 'text/plain': 'net'}

    uri_part = path
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


def redirect(request, path):    
    redir_response = HttpResponse('')
    redir_response.status_code = '303'
    redir_response['Location'] = 'http://doc.metalex.eu/doc/{0}'.format(path)
    
    return redir_response



def check_available(bwbid, path, version):
    uri = '<http://doc.metalex.eu/id/{0}{1}{2}>'.format(bwbid, path, version)
    q = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX metalex: <http://www.metalex.eu/schema/1.0#>\nASK { "+uri+" rdf:type ?x .}"
    
    sparql = SPARQLWrapper("http://doc.metalex.eu:8000/sparql/")
    sparql.setQuery(q)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results['boolean']

    
def describe(path, format='rdf'):
    uri = '<http://doc.metalex.eu/id/{0}>'.format(path)
    q = "DESCRIBE {0}".format(uri)
    
    sparql = SPARQLWrapper("http://doc.metalex.eu:8000/sparql/")
    sparql.setQuery(q)
    
    cg = sparql.queryAndConvert()    
    
    cg = setNamespaces(cg)
    
    if format=='ttl' :
        response = HttpResponse(cg.serialize(format='turtle'))
        response['Content-Type'] = 'application/x-turtle'
    if format=='n3' :
        response = HttpResponse(cg.serialize(format='n3'))
        response['Content-Type'] = 'text/rdf+n3'
    elif format=='rdf' :
        response = HttpResponse(sparql.query())
        response['Content-Type'] = 'application/rdf+xml'
        
    return response
    
def setNamespaces(cg):
    # MetaLex
    MO = Namespace('http://www.metalex.eu/schema/1.0#')
    MS = Namespace('http://www.metalex.eu/schema/1.0#')    

    # Standard namespaces
    RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
    XML = Namespace('http://www.w3.org/XML/1998/namespace')
    OWL = Namespace('http://www.w3.org/2002/07/owl#')
    XHTML = Namespace('http://www.w3.org/1999/xhtml#')
    OPMV = Namespace('http://purl.org/net/opmv/ns#')
    TIME = Namespace('http://www.w3.org/2006/time#')
    DCTERMS = Namespace('http://purl.org/dc/terms/')
    FOAF = Namespace('http://xmlns.com/foaf/0.1/') 
    
    cg.namespace_manager.bind('mo',MO)
    cg.namespace_manager.bind('ms',MS)
    cg.namespace_manager.bind('xhtml',XHTML)
    cg.namespace_manager.bind('owl',OWL)
    cg.namespace_manager.bind('xml',XML)
    cg.namespace_manager.bind('rdfs',RDFS)
    cg.namespace_manager.bind('opmv',OPMV)
    cg.namespace_manager.bind('time',TIME)
    cg.namespace_manager.bind('dcterms',DCTERMS)
    cg.namespace_manager.bind('foaf',FOAF)
    
    return cg
    
    
    
    
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
    
    