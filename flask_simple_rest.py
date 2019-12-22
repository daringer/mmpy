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

class FlaskSimpleRest:
    """
    Shorter, fancier, http-method-driven app-routing, usage:

      @rest.get("/my/url/<int:foo>/endpoint")
      def my_view(foo, opt_arg=None):
          return jsonify({"some_data": 123})
    """
    def __init__(self, flask_app):
        self.app = flask_app

    def __getattr__(self, key):
        return self._wrap(key)

    def _wrap(self, method):
        @functools.wraps(self.app.route)
        def func(*v, **kw):
            kw["methods"] = [method.upper()]
            return self.app.route(*v, **kw)
        return func

def get_rest_decorator(app):
    return FlaskSimpleRest(app)

# woho, brain-shrinking 8-liner, pythonic-fanciness including brain-damage
# wrapping decorator aliases its arguments based on the decorating method/alias name
# @TODO: another (sub-)closure to apply jsonify breaks it, help, why?
# @FIXME: an instance is needed, could __call__ be used?
