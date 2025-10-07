from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

def init_security_headers(app: Flask):
    """Инициализация security headers"""
    
    @app.after_request
    def set_security_headers(response):
        # Защита от XSS
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CSP (Content Security Policy)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        # HSTS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    # Для работы за reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)