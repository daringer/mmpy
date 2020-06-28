"""
(REsTful) APIs building with flask made easy:
- just decorate any function to make it REsT-ready
- short notation and easily readable
- anything else as expected, including func-params

Example:

@rest.get("/items")
def my_endpoint():
    # ensured that only "GET" may be used for the web-request
    pass

@rest.post("/my/form/action")
def my_post_endpoint():
    # only POST will end here,
    # DELETE, PUT are also avaialble
    pass
"""


# @TODO @FIXME, shall we have a special endpoint which might deliver generic info?
# would need specific decorator to mark the function to be used ....
#endpoints.append((base_url)


######### aahhhhhhh, I guess I will end in hell for this code....

import os
import sys
import functools
import inspect
from pathlib import Path
from traceback import extract_stack

from .url_generator import get_urls_from_func


class FlaskAutoRoute:
    """
    Shorter, fancier, http-method-driven app-routing, usage:

      @rest.get("/my/url/<int:foo>/endpoint")
      def my_view(foo, opt_arg=None):
          return jsonify({"some_data": 123})
    """
    def __init__(self, flask_app, endpoint_root=None):
        """
        ........
        """
        self.app = flask_app
        self.endpoints = []
        self.auto_root_path = Path(endpoint_root).absolute() if endpoint_root else None

    def __getattr__(self, key):
        """`key` is the designated http.method, dynamically handled here"""
        # @TODO: feels like we should restrict this to key in ["get", "post", ...]
        #        and if not 'in' raise AttributeError()
        return self._wrap(key)

    def _wrap(self, http_method, auto_gen=False):
        """
        called by `__getattr__` like: `obj.stuff` with 'stuff' passed as 'http_method'.
        so '_wrap' is **returning a callable** compareable to calls, only dynamically:
            'rest_mgr.get(*v, **kw)', 'rest_mgr.post(*v, **kw)'
        """
        @functools.wraps(self.app.route)
        def func(*v, **kw):
            """for manual 'url' setting, directly returns the result of `app.route(*v, **kw)`"""
            kw["methods"] = [http_method.upper()]

            # any data in 'v' (a func-param) implies non-auto mode:
            if len(v) > 0:
                self.endpoints.append((v, kw))
                return self.app.route(*v, **kw)

            # empty function params => fallback to automated URL generation
            @functools.wraps(func)
            def sub_func(f):
                """*url-gen* requires func-obj, next wrap: `sub_func`, provides `f`"""
                # 'f' is what normally 'app.route' would have been called with for decoration
                _gen = (p.as_posix() for p in get_urls_from_func(f, self.auto_root_path))
                for url in _gen:
                    # apply some url-consistency stuff, just to be sure
                    url = url.replace("_", "-").replace(" ", "").lower()

                    self.endpoints.append((url, kw))
                    # *circle-wrap* (decorate) `f` for `len(endpoints)` times...
                    f = self.app.route(url, **kw)(f)
                return f
            return sub_func
        return func

def get_route_decorator(app, root_path):
    """shortcut function to be used for easy importing"""
    return FlaskAutoRoute(app, root_path)


