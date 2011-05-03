'''
Created on 28 Apr 2011

@author: hoekstra

Thanks to http://djangosnippets.org/snippets/1042/
'''


def parse_accept_header(accept):
    """Parse the Accept header *accept*, returning a list with pairs of
    (media_type, q_value), ordered by q values.
    """
    result = []
    for media_range in accept.split(","):
        parts = media_range.split(";")
        media_type = parts.pop(0)
        media_params = []
        q = 1.0
        for part in parts:
            (key, value) = part.lstrip().split("=", 1)
            if key == "q":
                q = float(value)
            else:
                media_params.append((key, value))
        result.append((media_type, tuple(media_params), q))
    result.sort(lambda x, y: -cmp(x[2], y[2]))
    return result

class AcceptMiddleware(object):
    def process_request(self, request):
        accept = parse_accept_header(request.META.get("HTTP_ACCEPT", ""))
        request.accept = accept
        request.accepted_types = map(lambda (t, p, q): t, accept)