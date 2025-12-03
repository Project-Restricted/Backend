from django.conf import settings
from django.http import HttpResponse, Http404
from pathlib import Path


def auth_test(request):
    """Serve the local docs/auth_test.html file for development/demo purposes.

    This makes the test page available under the same origin as the API
    (http://127.0.0.1:8000/auth-test/), so cookie-based flows can be tested
    without cross-site cookie restrictions.
    """
    docs_path = Path(settings.BASE_DIR).parent / 'docs' / 'auth_test.html'
    if not docs_path.exists():
        raise Http404('auth_test.html not found')
    content = docs_path.read_text(encoding='utf-8')
    return HttpResponse(content, content_type='text/html')
