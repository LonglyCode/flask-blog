from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors, sitemap, admins
from ..models import Permission
from forms import SearchForm


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission,form=SearchForm())
