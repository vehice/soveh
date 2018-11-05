"""
.. module:: utils.functions
   :synopsis: Generic functions used throughout the site.
"""

import json
from django.http import HttpResponse


def renderjson(data, status=200):
    return HttpResponse(
        json.dumps(data, separators=(",", ":")),
        content_type="application/json",
        status=status)