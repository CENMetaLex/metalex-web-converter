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

@summary: Django views for responding to requests for MetaLex resources
'''

from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from django.template.loader import get_template
from django.template import RequestContext
from rdflib import Namespace
from forms import QueryForm
import re
#from BeautifulSoup import BeautifulStoneSoup
from lxml import etree
import glob


# NB: Set these to point to the appropriate locations for the files generated by the metalex converter.
FILES_URL = "http://doc.metalex.eu/files/"
FILES_DIR = "/var/metalex/store/data/"
STYLED_FILES_DIR = "/var/metalex/store/styled-data/"

SPARQL_ENDPOINT = "http://doc.metalex.eu:8000/sparql/"

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
            
            SELECT DISTINCT ?uri ?title ?date ?xml ?event_type WHERE {
               ?uri a metalex:BibliographicExpression .
               ?uri dcterms:valid ?date .
               ?uri dcterms:title ?title .
               ?uri foaf:page ?xml .
               ?uri metalex:resultOf ?event .
               ?event a ?event_type .
               FILTER (regex(str(?title),\""""+title+"""\", "i") && regex(str(?event_type),"bwb","i") && (xsd:dateTime(?date) <= xsd:dateTime(\""""+str(date)+"""\")))
            } ORDER BY ?date"""
            
            

            sparql = SPARQLWrapper(SPARQL_ENDPOINT)
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
    if(path.startswith('ontology')) :
        type = 'bwb'
    else:
        type = 'id'
    
    if (format == 'html') :
        html_response = HttpResponse('')
        html_response.status_code = 302
        html_response['Location'] = 'http://www5.wiwiss.fu-berlin.de/marbles?uri=http://doc.metalex.eu/{0}/{1}'.format(type,path)
                
        return html_response   
    else :
        return describe(request, type, path, format)

def prepare_xml_expression(request,bwbid, path, version):
    # If our path consists solely of one of the known languages, then we're dealing with an entire regulation, 
    # and the language tag should not be considered as part of the filename.
    if re.search(r'^/(en|pl|de|fr|pt|ru|cs|zh|ne|nl|ar|fj|es)/$',path) is not None:
        path_underscore = '_'
    else :
        path_underscore = path.replace('/','_')
    
    expression_filename = '{0}{1}{2}{3}.xml'.format(bwbid, path_underscore, version, '_ml') 
    expression_filename_css = '{0}{1}{2}{3}.xml'.format(bwbid, path_underscore, version, '_mls') 
    expression_filepath = '{0}{1}'.format(FILES_DIR, expression_filename)
    expression_filepath_css = '{0}{1}'.format(STYLED_FILES_DIR, expression_filename_css)
    
    pi = '<?xml-stylesheet type="text/css" href="http://doc.metalex.eu/static/css/metalex.css"?>\n'
    
    # If an expression with style information already exists, return it
    if len(glob.glob(expression_filepath_css)) > 0 :
        return (expression_filename_css, None)
    # If no styled expression exists, but the expression itself does, return a stylised version.
    elif len(glob.glob(expression_filepath)) > 0 :
        with file(expression_filepath, 'r') as original: data = original.readlines()
        
        # ... need to skip the processing instruction.
        with file(expression_filepath_css, 'w') as modified: 
            modified.write(data[0] + pi)
            for l in data[1:] :
                modified.write(l)
        
        return (expression_filename_css, None)
    # Else, the expression does not exist, so we will need to extract it.
    else :
        uri = 'http://doc.metalex.eu/id/{0}{1}{2}'.format(bwbid, path, version)


        parent_expression_filename = '{0}{1}_{2}{3}.xml'.format(FILES_DIR,bwbid,version,'_ml')
        
        
        # We will be using lxml, BeautifulStoneSoup has too many problems with self closing tags.
        tree = etree.parse(parent_expression_filename)
        # DON'T Parse the document using BeautifulStoneSoup, but don't forget to specify potential self closing tags.
#        bss = BeautifulStoneSoup(open(parent_expressio/n_filename,'r'), selfClosingTags=['mcontainer','milestone'])

        # You can test this with http://doc.metalex.eu/id/BWBR0017869/hoofdstuk/I/artikel/1/2009-10-23/data.xml

        # We will be checking first for the transparent URI
        expression_content = tree.xpath(".//*[@about='{}']".format(uri))
#        expression_content = bss.findAll(attrs={"about" : uri})
        if len(expression_content) < 1 :
            # Apparently no transparent URI was found in the file, so need to find its corresponding opaque URI (NB: this could be multiple!)
            q = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?x WHERE {
            <"""+uri+"""> owl:sameAs ?x
        }"""
            
            sparql = SPARQLWrapper(SPARQL_ENDPOINT)
            sparql.setQuery(q)
            
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            
            
            try :
                opaque_uri = results["results"]["bindings"][0]["x"]["value"] 
                
#                expression_content = bss.findAll(attrs={"about" : opaque_uri})
                expression_content = tree.xpath(".//*[@about='{}']".format(opaque_uri))
            except :
                t = get_template('message.html')
                html = t.render(RequestContext(request, { 'title': 'Oops', 'text' : 'No opaque URI found for this transparent expression URI.\nFilename: {0}\n Hierarchical path: >{1}<'.format(expression_filename, path)}))
                return (None, HttpResponse(html))        

        
        expression_file = open(expression_filepath_css,'w')
        expression_file.write(pi)
        expression_file.write('<!-- URI: {0} -->\n'.format(uri))
        if opaque_uri is not None:
            expression_file.write('<!-- Opaque URI: {0} -->\n'.format(opaque_uri))
        expression_file.write('<root name="root">\n')
        for c in expression_content :
            expression_file.write(etree.tostring(c, pretty_print=True))
 
        expression_file.write('</root>')       
        expression_file.close()

        return (expression_filename_css, None)
        
        
        

def expression_data(request, bwbid, path, version, format):
    if (format == 'net') :
        if check_available(bwbid, path, version) :
            response = HttpResponse('')  
            response.status_code = 302
            response['Location'] = '{0}{1}_{2}.{3}'.format(FILES_URL, bwbid,version,format)
                
            return response
        else :
            t = get_template('not_converted.html')
            html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : version}))
            return HttpResponse(html)    
    elif (format == 'xml') :
        if check_available(bwbid, path, version) :
            response = HttpResponse('')
            response.status_code = 302
            
            (expression_filename, httpresponse) = prepare_xml_expression(request, bwbid, path, version)
            
#            expression_filename = '{0}_{1}{2}.{3}'.format(bwbid, version, '_ml', format)
            
            if httpresponse is None : 
                response['Location'] = '{0}{1}'.format(FILES_URL, expression_filename)
                return response
            else :
                return httpresponse
        else :
            t = get_template('not_converted.html')
            html = t.render(RequestContext(request, {'bwb' : bwbid, 'path' : path, 'version' : version}))
            return HttpResponse(html)
    elif (format == 'rdf' or format == 'n3' or format == 'ttl') :
        return describe(request, 'id', bwbid + path + version, format)
    elif (format == 'html') :
        if check_available(bwbid, path, version) :
            html_response = HttpResponse('')
            html_response.status_code = 302
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
        return describe(request, 'id', bwbid + path, format)
    elif (format == 'html') :
        if check_available(bwbid, path, '') :
            html_response = HttpResponse('')
            html_response.status_code = 302
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
            response.status_code = 302
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

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(q)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    
    try :
        result = results["results"]["bindings"][0]["x"]["value"] 
        
        redir_response = HttpResponse('')
        redir_response.status_code = 303
        redir_response['Location'] = result
        
        return redir_response
    except :
        t = get_template('message.html')
        html = t.render(RequestContext(request, { 'title': 'Oops', 'text' : 'No expression found for this work URI.'}))
        return HttpResponse(html)


def redirect(request, path):    
    redir_response = HttpResponse('')
    redir_response.status_code = 303
    redir_response['Location'] = 'http://doc.metalex.eu/doc/{0}'.format(path)
    
    return redir_response



def check_available(bwbid, path, version):
    uri = '<http://doc.metalex.eu/id/{0}{1}{2}>'.format(bwbid, path, version)
    q = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX metalex: <http://www.metalex.eu/schema/1.0#>
    
    ASK { 
        { """+uri+""" ?p ?x .} UNION { ?x ?p """+uri+""" .} 
    }"""
    
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(q)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results['boolean']

    
def describe(request, type, path, format='rdf'):
    uri = '<http://doc.metalex.eu/{0}/{1}>'.format(type, path)
#    q = "DESCRIBE {0}".format(uri)

    # Get a symmetric concise bounded description (SCBD)
    q = "CONSTRUCT {"+uri+" ?p ?o . ?s ?p2 "+uri+" .} WHERE { {"+uri+" ?p ?o .} UNION {?s ?p2 "+uri+" .} }"
    
    
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(q)
    
    cg = sparql.queryAndConvert()    
    
    cg = setNamespaces(cg)
    
    if format=='ttl' :
        response = HttpResponse(cg.serialize(format='turtle'))
        response['Content-Type'] = 'application/x-turtle'
    elif format=='n3' :
        response = HttpResponse(cg.serialize(format='n3'))
        response['Content-Type'] = 'text/rdf+n3'
    elif format=='rdf' :
        response = HttpResponse(sparql.query())
        response['Content-Type'] = 'application/rdf+xml'
    else :
        t = get_template('message.html')
        html = t.render(RequestContext(request, { 'title': 'Oops', 'text' : 'We do not serve content of this type for this URI'}))
        return HttpResponse(html)        
        
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
    SEM = Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/')
    
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
    cg.namespace_manager.bind('sem',SEM)
    
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
    
    