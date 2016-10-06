from flask import render_template,make_response,url_for
import datetime
from . import main
from ..models import Post,Category

@main.route('/sitemap.xsl/')
def sitemap_xsl():
    response = make_response(render_template('sitemap.xsl'))
    response.mimetype = 'text/atom+xsl'
    return response

@main.route('/sitemap.xml/', methods=['GET'])
def sitemap_xml():

    urlset = []

    urlset.append(dict(
        loc=url_for('main.index', _external=True),
        lastmod=datetime.date.today().isoformat(),
        changefreq='weekly',
        priority=1,
    ))

    categories = Category.query.all()

    for category in categories:
        urlset.append(dict(
            loc=category.link,
            changefreq='weekly',
            priority=0.8,
        ))

    posts= Post.query.public().all()

    for post in posts:
        url = post.link
        modified_time = post.modified_time.date().isoformat()
        urlset.append(dict(
            loc=url,
            lastmod=modified_time,
            changefreq='monthly',
            priority=0.5,
        ))

    sitemap_xml = render_template('sitemap.xml', urlset=urlset)
    res = make_response(sitemap_xml)
    res.headers['Content-type'] = 'application/xml; charset=utf-8'
    return res
