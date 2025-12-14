from django.conf import settings
from django.http import HttpResponse, Http404
from pathlib import Path


def auth_test(request):
    """Auth test page removed.

    The interactive auth test page was removed during docs cleanup. Raise
    404 to avoid serving a missing file and point consumers to the canonical
    API specification (`API_ENDPOINTS.md` at the repository root).
    """
    raise Http404('auth_test.html removed; see API_ENDPOINTS.md')
