import os
import inspect
from pathlib import Path


type_map = {
   "int"                     : "int",
   "float"                   : "float",
   "str"                     : "string",
   Path().__class__.__name__ : "path"
}

class NotBelowRootPathError(Exception): pass

def get_urls_from_func(func, root_path=None, func_name=None, fail_base=None):
    """
    # automatically generate a unique URL for any provided callable `func`.

    ## args:
      `func`      => the target callable, for which URLs will be generated
      `root_path` => a filesystem path, on auto-generation all targets shall
                     be below this dir (see `fail_base`)
      `func_name` => take the provided name instead of the one derived
      `fail_base` => any `func` with a srcfile not below `root_path`,
                     will get `fail_base` as replacement for the
                     token, which would normally be the relative-dir

    ## how it works:
    1) get src-path for `func` and check it's feasibility & reachability
       w.r.t. `root_path` => `base_path` (relative (to root) path)
    2) parse func's args into 3 groups as documented inside the `middle docstr`.
       arg -annotations (typing), -ordering, -defaults are fully taken into
       consideration for *url* generation
    3) assemble `urls` by rendering the param classes (`v-`, `kw-`, `h-`) like this:
       * `[v-args]` are *fully ordered* & *typed*, thus form the `base_url` i.e.:
         `/<src-rel-path>/<function-name>/<arg1>/../<argN>/`
         `arg1 ... argN` are mandatory -> must be included (no defaults)
       * `[kw-args]` are in order, appended (cumulative) one after another to the `base_url`
         leading to `n`-copies of the URL, with `n == len(kw-args)`
    """

    # get function's source filename (+path) and strip ".py" suffix ...
    call_src_fn = inspect.getfile(func)
    base_path = Path(call_src_fn[:call_src_fn.rfind(".")])
    rel_path = None
    # ... and determine + ensure rel-path w.r.t. 'root_path'
    try:
        rel_path = base_path.relative_to(root_path)
    except (ValueError, TypeError) as e:
        if fail_base is None and root_path is not None:
            raise NotBelowRootPathError((call_src_fn, root_path, func))

        if fail_base:
            # be picky about trailing slashes ...
            rel_path = fail_base
            while "/" in rel_path:
                rel_path = rel_path[1:] if rel_path.startswith("/") else rel_path

    # func's endpoints collection
    endpoints = []

    """
    derive func-parameters to url-arguments mapping:
    [v-args]   add as 'path' in endpoint-url and ensure name + type-annotations are used
    [kw-args]  fork an endpoint for each one with an default arg: one default arg, next: two ....
    [h-kwargs] (marked as hidden, if startswith("_")] will simple be skipped but saved
    """
    p_url, p_url_kw, p_hidden = [], [], []
    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        # keep hidden params and continue ...
        if name.startswith("_"):
            p_hidden.append(param)
            continue

        # construct url using name + type
        _type = (type_map[param.annotation.__name__] + ":") \
                    if param.annotation != inspect._empty else ""
        box = (p_url if param.default == inspect._empty else p_url_kw)
        box.append(f"<{_type}{name}>")

    # assemble base_url ("/" + rel-path + func_name)
    func_name = func_name or func.__name__
    base_url = os.path.sep / rel_path / func_name

    # join params (p1, p2, ..., pN) to '{p1}/{p2}/.../{pN}' and ...
    p_url_suffix = os.path.join(*p_url) if len(p_url) > 0 else ""
    assert len(sig.parameters) == len(p_url) + len(p_url_kw) + len(p_hidden)

    # ...append to 'base_url',  leading to the 1st complete endpoint
    endpoints.append(base_url / p_url_suffix)

    # further fork endpoints in ORDER of kw-params (params with defaults)
    for idx, _ in enumerate(p_url_kw):
        endpoints.append(base_url / p_url_suffix / os.path.join(*p_url_kw[:idx+1]))

    # @TODO: instead of cumulative-auto-url forking we could add all permutations of the
    #        optional kw-params: more urls, higher 'comfort'---but what about ambiguity?

    return endpoints

