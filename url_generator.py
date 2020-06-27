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

# @TODO @FIXME: find another place (more generic functionality actually) for this
#               piece of 'art': function is class independent, only args needed
def get_urls_from_func(func, root_path, force_func_name=None):
    """
    automatically generate a unique URL for any provided callable `func`.

    requires: `func`'s src-file must be below `root_path`

    how it works:
    1) get sourcepath for `func` and check it's feasibility & reachability
       w.r.t. `root_path` => `base_path` (relative (to root) path)
    2) parse function's args into 3 groups as documented inside the `middle docstr`.
       arg -annotations (typing), -ordering, -defaults are fully taken into
       consideration for *url* generation
    3) all parts are now assembled together to a proper `url`. The different func
       param classes (`v-`, `kw-`, `h-`) are handled like this:
       * `[v-args]` are rendered *fully ordered* & *typed* and form together the
         `base_url` like this: `/<src-rel-path>/<function-name>/<arg1>/../<argN>/`
         `arg1 ... argN` are mandatory, thus included (no default provided)
       * `[kw-args]` are kept in order to append one after another to the `base_url`
         leading to `n`-copies of the URL, with `n == len(kw-args)`
    4) return endpoints/urls
    """

    # get function's source filename (+path) and strip ".py" suffix ...
    call_from_path = inspect.getfile(func)

    dot_pos = call_from_path.rfind(".")
    base_path = Path(call_from_path[:dot_pos])
    # ... and determine + ensure rel-path w.r.t. 'root_path'
    try:
        rel_path = base_path.relative_to(root_path)
    except ValueError as e:
        print(f"[E] provided 'callable': '{force_func_name or func.__name__}' ")
        print(f"[E] src-file: '{call_from_path}'")
        print(f"[E] ==> IS NOT BELOW '{root_path}'")
        print(f"[E] aborting url_generation for this 'func'")
        raise NotBelowRootPathError((call_from_path, root_path, func))

    # func's endpoints collection
    endpoints = []

    """
    derive func-parameters to url-arguments mapping:
    [v-args]   add as 'path' in endpoint-url and ensure
               name + type-annotations are used
    [kw-args]  fork to multiple endpoints, regular one: w/o any default args.
               next: one default arg, next: two ....
    [h-kwargs] (marked as hidden, if startswith("_")] will not be used for
               endpoint-url generation, thus skipped, but still kept for later
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
    func_name = force_func_name or func.__name__
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

