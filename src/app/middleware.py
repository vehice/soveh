from utils import functions as fn
class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # LUEGO SETEAR AL VALOR A PARTIR DEL USER
        request.lang = fn.translation('es')

        response = self.get_response(request)

        return response