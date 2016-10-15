from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from os.path import splitext
import time
from app import db
from ..models import Post

__all__=['FileWatch']

class FileWatch(FileSystemEventHandler):

    def __init__(self,app=None):
        self._type = None
        self._path = None
        self.observer=Observer()
        if app is not None:
            self.init_app(app)

    def init_app(self,app):
        self.app=app
        self.run()

    def run(self):
        self.observer.schedule(
            self,
            path=self.app.config["CONTENT_PATH"],
            recursive=True
        )
        self.observer.start()

        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     self.observer.stop()
        # self.observer.join()

    def on_any_event(self,event):
        self._path =event.src_path
        self._type = splitext(self._path)[1]

    def on_created(self,event):
        if self._type ==".md":
            print "add a new markdown file,%s"%self._path
        elif self._type == ".html":
            print "add a new html file,%s"%self._path

    def on_deleted(self, event):
        if self._type ==".md":
            print "delete markdown file,%s"%self._path
        elif self._type == ".html":
            print "delete html file,%s"%self._path

    def on_modified(self, event):
        if self._type ==".md":
            print "modified a new markdown file,%s"%self._path
        elif self._type == ".html":
            print "modified a new html file,%s"%self._path

    def write_database(self):
        if self._type ==".md":
            print "modified a new markdown file,%s"%self._path
        elif self._type == ".html":
            print "modified a new html file,%s"%self._path
