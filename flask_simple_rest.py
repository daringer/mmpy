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

# @TODO: another (sub-)closure to apply jsonify breaks it, help, why?
# @FIXME: an instance is needed, could __call__ be used?


### @TODO, @FIXME
### fantasic IDEA to have a single class for both:
### - manual endpoints and
### - automated...
### @TODO @FIXME @CLEANUP


# @TODO @FIXME, shall we have a special endpoint which might deliver generic info?
# would need specific decorator to mark the function to be used ....
#endpoints.append((base_url)



######### I guess I will end in hell for this code....



import os
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
        self.auto_endpoint = auto_endpoint
        self.type_map = {}

        self.endpoints = []

        if self.auto_endpoint:
            assert endpoint_root
            self.root_path = Path(endpoint_root).absolute()
            self.type_map = {
                "int"                     : "int",
                "float"                   : "float",
                "str"                     : "string",
                Path().__class__.__name__ : "path"
            }

    def __getattr__(self, key):
        # if endpoint is passed as parameter, wrap only once
        if self.root_path is None:
            return self._wrap(key)
        # otherwise, fancier decoration of func w/o calling-parenthesis: ()
        else:
            return self._wrap(key)()

    def _wrap(self, method):

        @functools.wraps(self.app.route)
        def func(*v, **kw):
            kw["methods"] = [method.upper()]

            # if `auto_endpoint` go for generation of endpoints
            if self.auto_endpoint:
                # to actually get the function passed to `app.route`, we need another
                # level of func-wrapping, wohoo...
                @functools.wraps(func)
                def sub_func(f):
                    endpoints = self.gen_endpoints(f)
                    #out = f
                    for endpoint in endpoints:
                        #print(f)
                        #print(f"calling app.route({endpoint.as_posix()}, {kw}")
                        self.endpoints.append((endpoint.as_posix(), kw))
                        f = self.app.route(endpoint.as_posix(), **kw)(f)
                    return f
                return sub_func

            # otherwise a url/endpoint is expected to be provided (*v)
            else:
                # regular wrap (depth: 1) for `app.route`
                self.endpoints.append((v, kw))
                return self.app.route(*v, **kw)

        return func

    def gen_endpoints(self, wrapping_func):
        ## find function calling me using the call-stack...
        #stack = extract_stack()
        #my_call, others = stack[-1], stack[:-1]
        #assert len(others) > 0, "????"

        ## traverse stack up until 'not-me' file is found, its func is the caller
        #external_caller = None
        #while not external_caller:
        #    caller = others.pop()
        #    if caller.filename != my_call.filename:
        #        external_caller = caller
        #        break

        # strip ".py" suffix ...
        call_from_path = inspect.getfile(wrapping_func)
        dot_pos = call_from_path.rfind(".")
        base_path = Path(call_from_path[:dot_pos])
        # ... and determine relative path w.r.t. 'self.root_path'
        try:
            rel_path = base_path.relative_to(self.root_path)
        except ValueError as e:
            print("HANDLE FAILING REL-PATH DETERMINATION")
            raise e

        # all endpoints for this function will be collected here!
        endpoints = []

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
        p_url_suffix = os.path.join(*p_url) if len(p_url) > 0 else ""
        assert len(sig.parameters) == len(p_url) + len(p_url_extra) + len(p_hidden)

        # get endpoint `basename` using `wrapping_func`'s (function)-name
        funcname = wrapping_func.__name__
        base_url = os.path.sep / rel_path / funcname


        # basic endpoint without any default parameters included in url
        endpoints.append(base_url / p_url_suffix)
        # further fork endpoints in ORDER of kw-params (params with defaults)
        for idx, _ in enumerate(p_url_extra):
            endpoints.append(base_url / p_url_suffix / os.path.join(*p_url_extra[:idx+1]))
        #print ("-"*50)
        #print ("REGISTERED:")
        #print (f" - function: '{funcname}()' ")
        #print (f" - func-param-sig: {sig.parameters}")
        #print (f" - from file: '{call_from_path}'")
        #print ("ENDPOINTS\n -", "\n - ".join(map(str, endpoints)))
        #print ("-"*50)
        return endpoints


def get_rest_decorator(app, *vargs, **kwargs):
    """get the main (rest)-decorator, examples: `mmpy.flask_simple_rest.__doc__`"""
    return FlaskSimpleRest(app, *vargs, **kwargs)

# better fitting name
FlaskFastRoute = FlaskSimpleRest
get_route_decorator = get_rest_decorator

