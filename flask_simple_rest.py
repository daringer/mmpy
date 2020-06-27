"""
REsTful APIs building with flask made easy:
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

import functools
import inspect

from pathlib import Path
from traceback import extract_stack

class FlaskSimpleRest:
    """
    Shorter, fancier, http-method-driven app-routing, usage:

      @rest.get("/my/url/<int:foo>/endpoint")
      def my_view(foo, opt_arg=None):
          return jsonify({"some_data": 123})
    """
    def __init__(self, flask_app, auto_endpoint=False, endpoint_root=None):
        self.app = flask_app
        self.root_path = None
        self.type_map = {}

        if auto_endpoint:
            assert endpoint_root
            self.root_path = Path(endpoint_root)
            self.type_map = {
                "int"                     : "int",
                "float"                   : "float",
                "str"                     : "string",
                Path().__class__.__name__ : "path"
            }

    def __getattr__(self, key):
        return self._wrap(key)

    def _wrap(self, method):
        self.gen_endpoints(method)

        @functools.wraps(self.app.route)
        def func(*v, **kw):
            kw["methods"] = [method.upper()]
            return self.app.route(*v, **kw)
        return func

    def gen_endpoints(self, wrapping_func):
        stack = extract_stack()
        my_call, others = stack[-1], stack[:-1]
        assert len(others) > 0, "????"
        rel_path = None
        try:
            rel_path = self.root_path.relative_to(external_caller.filename)
        except ValueError as e:
            print("HANDLE FAILING REL-PATH DETERMINATION")
            raise e

        endpoints = []

        # traverse stack up until not-me file is found, its func is the caller
        external_caller = None
        while not external_caller:
            caller = others.pop()
            if caller.filename != my_call.filename:
                external_caller = caller
                break

        # determine func-parameters to url-arguments mapping:
        # v-args: add as 'path' in endpoint-url and ensure
        #                        name + type-annotations are used
        # kw-args: fork to multiple endpoints, regular one: w/o any default args.
        #          next: one default arg, next: two ....
        # kw-args (starting with "_"): will not be used for endpoint-url generation,
        #                              (might be relevant for arg-skipping or POST data)
        p_url, p_url_extra, p_hidden = [], [], []
        sig = inspect.signature(wrapping_func)
        for name, param in sig.parameters.items():
            # keep hidden params and continue ...
            if name.startswith("_"):
                p_hidden.append(param)
                continue

            # construct url using name + type
            _type = (self.type_map[param.annotation.__name__] + ":") \
                        if param.annotation != inspect._empty else ""
            box = (p_url if param.default == inspect._empty else p_url_extra)
            box.append(f"<{_type}{name}>")
        p_url_suffix = os.path.join(*p_url)
        assert len(sig.parameters) == len(p_url) + len(p_url_extra) + len(p_hidden)

        # get endpoint `basename` using `wrapping_func`'s (function)-name
        funcname = wrapping_func.__name__
        base_url = os.path.sep / rel_path.as_posix / funcname

        # @TODO @FIXME, shall we have a special endpoint which might deliver info?
        # would need specific decorator to mark the function to be used ....
        #endpoints.append((base_ur)

        # basic endpoint without any default parameters included in url
        endpoints.append(base_url / p_url_suffix)
        # further fork endpoints in ORDER of kw-params (params with defaults)
        for idx, _ in enumerate(p_url_extra):
            endpoints.append(base_url / p_url_suffix / os.path.join(*p_url_extra[:idx+1]))

        print ("ENDPOINTS", "\n".join(endpoints))
        return endpoints


def get_rest_decorator(app):
    """get the main (rest)-decorator, examples: `mmpy.flask_simple_rest.__doc__`"""
    return FlaskSimpleRest(app)

def get_method_decorators(app, methods=None):
    """
    Similar to `get_rest_decorator`, but return multiple decorators w/o the rest-obj.
      - default `methods`: get, post, put, delete
    """
    methods = methods or ["get", "post", "put", "delete"]
    rest = FlaskSimpleRest(app)
    return [getattr(rest, meth) for meth in methods]







# woho, brain-shrinking 8-liner, pythonic-fanciness including brain-damage
# wrapping decorator aliases its arguments based on the decorating method/alias name
# @TODO: another (sub-)closure to apply jsonify breaks it, help, why?
# @FIXME: an instance is needed, could __call__ be used?
