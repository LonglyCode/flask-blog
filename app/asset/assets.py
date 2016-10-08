from webassets.filter import get_filter
from flask.ext.assets import Environment, Bundle

bundles ={
    'all_js': Bundle(
        'vendor/semantic/dist/semantic.min.js',
        filters='jsmin',
        output='js/all.min.js'),

    'all_css': Bundle(
        'vendor/semantic/dist/semantic.css',
        filters='cssmin',
        output='css/all.min.css'),
}

def init_app(app):
    webassets =Environment(app)
    webassets.register(bundles)
    webassets.manifest = 'cache' if not app.debug else False
    webassets.cache = not app.debug
    webassets.debug = app.debug