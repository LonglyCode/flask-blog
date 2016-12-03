# 一个网站的诞生

## 前言

之前用github结合hexo搭建过静态博客，但出现过很多问题，比如前期样式设置总是要翻阅各种文档，虽然文档不一而足，多数都是互相抄袭借鉴，在复制配置的过程中也是不知所以然。此外，现在经常会使用平板或者手机浏览自己博客，发现一些拼写错误想直接修改；在每篇文章下有了新的评论也没有及时通知机制，别人想给你讨论互动也不得其道。还有更换了电脑之后也不知道怎么迁移，因为有段时间比较忙，所以博客也就搁置了很长时间。诸多种种，让我放弃继续维护静态博客的念头。当然静态博客还是有许多优势，比如提供了免费的域名空间，样式一配置好效果马上出来等。它只不过不满足我的需求了，在我看来博客除了自我总结之外也是一种和别人交流知识的渠道，想更加长期稳定地维护一个博客系统，所以不能只是知其然了。
    另一原因是学习了flask等框架，磨刀霍霍想试手做出一个博客系统来。其实在网上已经有了很多类似的教程，还有全面《flask web开发》等一书，不过大多都是面向入门的，供初级学习参考用。再写这些重复的知识点是没意义的，所以这篇文章不是针对入门的开发者，而是对flask开发博客过程中的进阶总结，会涵盖之前没有的知识点，比如一个网站常见用的中文全文搜索、后台管理、网站地图、提供订阅等。flask看起来是微型的框架，真的很容易上手。核心微型，但实际用起来围绕这个核心拓展还是有比较多的坑，好比一个需要组装的玩具，需要耐心来挖坑和填坑。
    这个博客如上所述后端使用flask，前端使用semantic-ui。
    
## 初始化
项目结构主要还是直接拿《flask web开发》一书中**flasky**这个博客系统组织方式，之前看过大大小小的flask项目，还是**flasky**配置方式比较灵活简单，书里已经说明得很清楚，这里再按自己理解阐述一下。

### config文件
这个文件主要定义一个`Config`类，在类里面定义各种配置字段的值，比如常见的字段`SECRET_KEY`。
```python
Class Config(object):
    SECRET_KEY = os.urandom(32)
    POST_PER_PAGE = 5
    SQLACHEMY_COMMIT_ON_TEARDOWN = True
    ......
    
    @staticmethod
    def init_app(app)
        pass
# 然后继承这个类来表示不同开发状态
Class DefaultConfig(Config):
    '''默认配置，新增指定了DEBUG与否与数据库的位置'''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///......data_default.sqlite'
    
Class DevelopmentConfig(Config):
    '''开发中配置'''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///......data_dev.sqlite'
    
Class ProductionConfig(Config):
    '''生产环境的配置'''
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///......data_pro.sqlite'
    
# 最好用一个字典将其导出
config = {
    'development':DevelopmentConfig,
    'prodution':ProductionConfig,
    'default':DefaultConfig
}
```
原理就是用类来表示枚举类型

### 在__init__插件初始化
在app应用文件夹下面的新建一个`__init__.py`让app变成一个包，这个包就是开发所在的空间了，然后这个包文件里用工厂模式来批量初始化依赖插件。

```python
from flask import Flask
from flask_sqlachemy import SQLAlchemy
from flask_mail import Mail
from flask_admin import Admin
from config import config # 在这里引入上一小节的config字典

db = SQLAlchemy()
mail = Mail()
admin = Admin()

def create_app(config_name):
    # 初始化 flask
    app = Flask(__name__)
    # from_object 函数可以直接将类中的属性转换成app配置 
    app.config.from_object(config[config_name])
    
    # 批量初始化插件
    db.init_app(app)
    admin.init_app(app)
    mail.init_app(app)
   
    # 同样可以批量引入并注册蓝图 
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
    
# 在manage.py文件里面动态的选择创建app
from app import create_app
app = create_app('default')
```
## 简单回顾MVC
虽然现在各种模式层出不穷，但多是MVC模式的演化，主流的框架也多是保留MVC模式。其实理解了MVC基本上你对主流的python web框架也就能信手拈来了。M代表的是Model，在python常用ORM来做数据库映射，一般都是大名鼎鼎的sqlalchemy和mysql结合来创建数据库；V是View，业务呈现层，一般指的是有HTML/CSS/JAVASCRIPT和模板结合而成的由服务器返回的HTML文件(这种定义有点狭隘)；C是Control，把Model和View结合起来，其实在flask中MVC太清晰了。
下面演示MVC构建的最小博客系统，在首页直接返回所有的文档，仅做参考用。

- Model
```python
# 在app包根目录下新建一个Model.py文件
from app import db # 此db就是sqlalchemy初始化后的对象
Class Post(db.Model):
    ''' 定义了主键id，标题title，主体body'''
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key = True
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
```
- View
```python
# 其实主要是jinja2的使用，在app下新建一个文件夹叫templates，在文件夹下面新建一个HTML文件，Posts.html
{% for post in posts %}
    <div class="posts">
    <h2> {{ post.title }} </h2>
    <p> {{ post.body }} </p>
    </div>
{% endfor %}
```
- Control
```python
from flask import Blueprint,render_template
from Model import Post 
# 注册一个蓝图
main = Blueprint('main',__name__)
# 指定访问路径为'/posts'
@main.route('/posts')
def posts()
    posts= Post.query.all()
    render_template('Posts.html',posts=posts)
```

## markdown支持
markdown 高亮的只是按着步骤来的，具体的细节没有深究，主要依赖`markdown`和`pygments`这两个库。后续再补充。

``` python
# 下面是render即渲染函数，文章的正文在新建的时候用此函数来渲染成html

import markdown
def markdown_render(text,codehilite=True):
    exts =[
        'abbr', 'attr_list', 'def_list', 'sane_lists', 'fenced_code',
        'tables', 'toc', 'wikilinks',
    ]

    if codehilite:
        # exts.append('codehilite(guess_lang=True,linenums=True)')
        exts.append('codehilite(guess_lang=True)')

    return Markup(markdown.markdown(
        text,
        extensions=exts,
        safe_mode=False,
    ))

# style可以选择pygments里面不同的风格
from pygments.formatters.html import HtmlFormatter
def pygments_style_defs(style='default'):
    formatter = HtmlFormatter(style=style)
    return formatter.get_style_defs('.codehilite')

# 然后定义需要引用的css文件路径，在这里选的是`monokai`风格的语法高亮
@main.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('monokai'),200,{'Content-Type':'text/css'}

```

最终只要在前端直接引用上面生成的css文件就是了

``` html
<head>
<link href="{{url_for('main.pygments_css')}}" rel="stylesheet" />
</head>
```
## 标签/栏目/归档
标签和博客文章是多对多的关系，栏目和文章是一对多，而且为了简单起见不进行栏目的分级了，归档是根据年份来分类就行了，有时间再改成月份。至于怎么设置关系的可以看本博客另外一篇关于`flask-sqlalchemy`总结文章。

### 标签
分别定义两个路径，一个是所有标签的集合界面，另外一个是单个标签的页面。

``` python
# 所有的标签的集合
@main.route('/tags',methods=['GET','POST'])
def tags_posts():
    tags = Tag.query.all()
    return render_template('tags.html',tags=tags)

# 单个标签路径
@main.route('/tags/<name>',methods=['GET','POST'])
def tag(name):
    tag = Tag.query.filter_by(name=name).first()
    return render_template('result.html',item=tag)

```
通过`tag.posts`直接获得某个标签下的所有的文章，`tag`是一个Tag对象。下面是前端简约代码。

``` html
<!-- 整个集合前端的代码，相当用了两个for循环来取出post -->
<div class="article-body">
        {% for t in tags %}
        <!-- t是单个tag对象 -->
                    {% for p in t.posts %}
                    <!-- 这里p 就代表一篇文章 -->
                    {% endfor %}
        {% endfor %}
</div>
<!-- 单个界面就更加简单了，在包含的里面的返回每篇文章的简介 -->
<div class="posts">
{% for post in item.posts %}
{% include "inside/post.html" %}
{% endfor %}
</div>
```

### 栏目和归档
栏目和归档类似和只是提取文章的某个单一属性，以这个属性为基准筛选出相关的所有文章。用`defaultdict`这个容器可以很好的解决问题。
``` python
from collections import defaultdict
@main.route('/categories',methods=['GET','POST'])
def categories_posts():
    posts = Post.query.all()
    d=defaultdict(list) # 默认的item类型为list
    for p in posts:
        d[p.category].append(p)
    return render_template('categories.html',d=d)
```

通过上面操作的可以得到类似的字典`{'key1':[post1,post2,post3],'key2':[post4,post5],...}`，然后在前端界面也可以通过两个for循环排版出每个栏目下面的所属的所有文章。

``` html
<div class="article-body">
        {% for key,value in d.items() %}
        <!-- key 代表了一个栏目 -->
                    {% for p in value %}
                    <!-- 这里p 就代表一篇文章 -->
                    {% endfor %}
        {% endfor %}
</div>
```

## 网站地图(sitemap)
网站地图其实提供一个`xml`文件给搜索引擎等使用，此功能可有可无。思路是维护一个`xml`文件，这个`xml`文件的格式一定要满足标准而且要预留填充的占字符，接着使用模板引擎将文章等信息的填充进去，和返回`html`文件差不多。

``` python
@main.route('/sitemap.xml/', methods=['GET']) # 这里的路径看起来像是访问一个文件一样
def sitemap_xml():
 
    urlset = []
    # 此网站的信息
    urlset.append(dict(
        loc=url_for('main.index', _external=True), # 设置_external参数，返回此网站主页的绝对链接
        lastmod=datetime.date.today().isoformat(),
        changefreq='weekly',
        priority=1, # 设置重要等级
    ))
    # 每个栏目以字典形式存入
    for category in Category.query.all():
        urlset.append(dict(
            loc=category.link,
            changefreq='weekly',
            priority=0.8,
        ))
    # 每篇文章同理以字典的形式存入
    for post in Post.query.all():
        url = post.link
        modified_time = post.modified_time.date().isoformat()
        urlset.append(dict(
            loc=url,
            lastmod=modified_time,
            changefreq='monthly',
            priority=0.5,
        ))

    sitemap_xml = render_template('sitemap.xml', urlset=urlset) # jijia2同样支持xml形式。
    res = make_response(sitemap_xml)
    res.headers['Content-type'] = 'application/xml; charset=utf-8' # 注意设置头信息为xml。
    return res
```

xml文件形式大概如下:
``` html 
<?xml version="1.0" encoding="UTF-8"?>
    <?xml-stylesheet type="text/xsl" href="{{ url_for('main.sitemap_xsl') }}"?>
        <urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"  xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0">
            {% for url in urlset -%}
            <url>
                <loc>{{ url['loc']|safe }}</loc>
                <mobile:mobile type="pc,mobile"/>
                {%- if 'lastmod' in url %}
                <lastmod>{{ url['lastmod'] }}</lastmod>{% endif %}
                {%- if 'changefreq' in url %}
                <changefreq>{{ url['changefreq'] }}</changefreq>{% endif %}
                {%- if 'priority' in url %}
                <priority>{{ url['priority'] }}</priority>{% endif %}</url>
            {% endfor -%}
        </urlset>
```
## 后台管理
`django`本身提供了一套完整易用的后台管理，实际没必要羡慕，`flask-admin`这个包提供了同样强大的功能。
### flask-admin简介
flask-admin提供了几个视图形式，只要继承这个几个视图类重写里面的方法或者属性就能呈现我们后台的数据库，比如说`AdminIndexView`是后台管理入口呈现界面的视图类，`ModelView`是针对**关系型**数据库的视图类，只要数据库某个表跟这个类挂钩就可以直接在网页上进行增删查改，`FileAdmin`是用来管理服务器上某个路径的文件。大概用法如下：

``` python
import db,Post
import app # flask应用实例
from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView

class PostAdmin(ModelView):
    pass
 
admin = Admin(name="xx")
admin.init_app(app)
# 以下进行view的注册。
admin.add_view(PostAdmin(Post, db.session, name='文章'))
```
通过访问 **主页/admin/** 就能进入后台管理了。
### flask-admin常用的功能
`flask-admin`在读了官方文档后发现已经实现也很多功能，不一而足，有些功能很常用。

``` python
class PostAdmin(ModelView):

    # 是否允许创建/编辑/删除Post实例
    can_create = True
    can_edit = True
    can_delete = True

    # 防止csrf攻击，设置默认Form
    from_base_class = SecureForm

    # 设置哪些列可以呈现/被搜索/可直接编辑/可筛选
    column_list = ('title','category','pub_time','published')
    column_searchable_list = ('title',)
    column_editable_list = ('title','slug')
    column_filters = ('category',)

    # 设置查看的权限，如果没有设置可能会导致后台泄露
    def is_accessible(self):
        return current_user.is_administrator()

    # 指定当没有权限时会返回到哪个界面
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index', page=1))
```

## 静态文件管理

### asset

### flask-asset

## 全文搜索
可以看到本博客尽量用python本身来实现除前端外的所有功能，不想引入谷歌搜索或者使用其他语言实现的全文索引引擎，`whoosh`是纯python 实现的全文索引，又因为要涉及到中文，所以肯定还要结合`jieba`分词，还好这两者结合非常好，最终搜索中文的效果也非常不错。
### flask_whooshalchemyplus
`flask_whooshalchemy`原本是结合的flask/whoosh/sqlalchemy 的库，但是不支持中文搜索，然后发现了`flask_whooshalchemyplus`可以支持中文。

``` python
# 初始化，app是一个flask实例
import flask_whooshalchemyplus
flask_whooshalchemyplus.init_app(app)
# 设置生成索引的位置
WHOOSH_BASE = os.path.join(somedir,'search.db') 
# 在文章类处指定可以被搜索字段
class Post(db.Model):
    __searchable__= ['body','title','slug']
    ......
# 手动生成索引
from flask_whooshalchemyplus import whoosh_index
whoosh_index(app,Post)
# 最终就可以用下面的方法进行全文搜索，query是一个关键词
posts = Post.query.whoosh_search(query).all()
```
### jieba
上一节只能进行英文搜索，要结合jieba分词才能进行中文全文搜索，设置非常简单，只要把jieba分析器加入到文章的`__analyzer__`字段上面就行了。

``` python
from jieba.analyse import ChineseAnalyzer
class Post(db.Model):
    __analyzer__=ChineseAnalyzer()
    ......
```
值得注意的是，把jieba引入过后最好把原来的索引生成的文件夹删除，重新生成索引。
## 提供订阅功能

### feed

## 博客分页功能

### paginate

## 文件监控

### watch-dog

## 部署

### gun

### nginx

### supervisor

### gevent

## 服务器/备案/域名

## TODO

### 缓冲

### logger和test

### 多说评论

### 网站流量分析

### 本地到远程部署

