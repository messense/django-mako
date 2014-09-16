from __future__ import absolute_import, unicode_literals
import posixpath
from mako.lookup import TemplateLookup as _MakoTemplateLookup
from mako.template import Template as DefaultTemplate


class TemplateLookup(_MakoTemplateLookup):

    def __init__(self, *args, **kwargs):
        self._template_class = kwargs.pop('template_class', DefaultTemplate)
        super(TemplateLookup, self).__init__(*args, **kwargs)

    def _load(self, filename, uri):
        self._mutex.acquire()
        try:
            try:
                # try returning from collection one
                # more time in case concurrent thread already loaded
                return self._collection[uri]
            except KeyError:
                pass
            try:
                if self.modulename_callable is not None:
                    module_filename = self.modulename_callable(filename, uri)
                else:
                    module_filename = None
                self._collection[uri] = template = self._template_class(
                    uri=uri,
                    filename=posixpath.normpath(filename),
                    lookup=self,
                    module_filename=module_filename,
                    **self.template_args
                )
                return template
            except:
                # if compilation fails etc, ensure
                # template is removed from collection,
                # re-raise
                self._collection.pop(uri, None)
                raise
        finally:
            self._mutex.release()

    def put_string(self, uri, text):
        """Place a new :class:`.Template` object into this
        :class:`.TemplateLookup`, based on the given string of
        ``text``.

        """
        self._collection[uri] = self._template_class(
            text,
            lookup=self,
            uri=uri,
            **self.template_args
        )
