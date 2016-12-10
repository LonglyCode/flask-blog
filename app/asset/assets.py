from flask_assets import Bundle, Environment
from webassets.filter import get_filter

bundles ={
    'all_js': Bundle(
        'js/jquery-2.1.4.min.js',
        'vendor/semantic/dist/semantic.min.js',
        filters='jsmin',
        output='js/all.min.js'),

    'all_css': Bundle(
        'vendor/semantic/dist/semantic.min.css',
        filters='cssmin',
        output='css/all.min.css'),
}

def init_app(app):
    webassets =Environment(app)
    webassets.register(bundles)
    webassets.manifest = 'cache' if not app.debug else False
    webassets.cache = not app.debug
    webassets.debug = app.debug
