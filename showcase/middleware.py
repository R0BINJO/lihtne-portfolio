CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' https:; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'"

class SecurityHeaders:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force host validation even on views that do not construct absolute URLs.
        request.get_host()
        response = self.get_response(request)
        response['Content-Security-Policy'] = CSP
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'
        response['Cache-Control'] = 'no-store'
        response['X-Frame-Options'] = 'DENY'
        return response
