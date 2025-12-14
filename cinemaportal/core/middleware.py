from django.http import HttpResponse


class CustomCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # For OPTIONS preflight return empty 200 with CORS headers
        if request.method == 'OPTIONS':
            resp = HttpResponse()
            origin = request.headers.get('Origin')
            if origin:
                resp["Access-Control-Allow-Origin"] = origin
            else:
                resp["Access-Control-Allow-Origin"] = "*"
            resp["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            resp["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-CSRFToken"
            resp["Access-Control-Allow-Credentials"] = "true"
            return resp

        response = self.get_response(request)
        origin = request.headers.get('Origin')
        if origin:
            response["Access-Control-Allow-Origin"] = origin
        else:
            response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-CSRFToken"
        response["Access-Control-Allow-Credentials"] = "true"
        return response