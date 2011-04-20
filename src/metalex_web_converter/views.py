'''
Created on 19 Apr 2011

@author: hoekstra
'''

from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON

def xml_data(request, bwbnr, doc, version):
    if check_available(bwbnr, doc, version) :
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://u017101.jur.uva.nl/files/BWB{0}_{1}_ml.xml'.format(bwbnr,version)
            
        return xml_response
    else :
        return HttpResponse("Document has not been converted yet ...")

def rdf_data(request, bwbnr, doc, version):
    if check_available(bwbnr, doc, version) :
        rdf_response = HttpResponse('')
        rdf_response.status_code = '302'
        rdf_response['Location'] = 'http://u017101.jur.uva.nl/files/BWB{0}_{1}.n3'.format(bwbnr,version)
            
        return rdf_response   
    else :
        return HttpResponse("Document has not been converted yet ...")

def html_data(request, bwbnr, doc, version):
    if check_available(bwbnr, doc, version) :
        rdf_response = HttpResponse('')
        rdf_response.status_code = '302'
        rdf_response['Location'] = 'http://u017101.jur.uva.nl:3020/browse/list_resource?r=http://doc.metalex.eu/BWB{0}/{1}/{2}'.format(bwbnr,doc,version)
            
        return rdf_response   
    else :
        return HttpResponse("Document has not been converted yet ...")


def negotiate(request, bwbnr, doc):
    accept_header = request.META['HTTP_ACCEPT']
    
    if accept_header.find('html') != -1:
        html_response = HttpResponse('')
        html_response.status_code = '302'
        html_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}/data.html'.format(bwbnr,doc)
        
        return html_response
    elif accept_header.startswith('application/rdf+xml' or accept_header.startswith('application/x-turtle') or accept_header.startswith('text/rdf+n3')) :        
        rdf_response = HttpResponse('')
        rdf_response.status_code = '302'
        rdf_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}/data.rdf'.format(bwbnr,doc)
        
        return rdf_response
    elif accept_header.startswith('application/xml') or accept_header.startswith('text/xml'):        
        xml_response = HttpResponse('')
        xml_response.status_code = '302'
        xml_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}/data.xml'.format(bwbnr,doc)
        
        return xml_response
    else :
        return HttpResponse("Accept header is: {0}".format(accept_header))

def redirect(request, bwbnr, doc):
    accept_header = request.META['HTTP_ACCEPT']
    
    redir_response = HttpResponse('')
    redir_response.status_code = '303'
    redir_response['Location'] = 'http://doc.metalex.eu/doc/BWB{0}/{1}'.format(bwbnr,doc)
    
    return redir_response


def check_available(bwbnr, doc, version):
    uri = '<http://doc.metalex.eu/BWB{0}/{1}{2}>'.format(bwbnr, doc, version)
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
    
    
    
    
    