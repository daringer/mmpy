
class FakeAttrChain:
    """
    collects (chains) arbitrary depth obj.attr-calls and reports them back via a call
    to 'callback', two ways to abort:

    - one of the attrs. is __call__-ed -> callback(self.__data, call=True)
    (1st option implies 'callback' returns a callable)

    - `'attr' in stop_keys' -> callback(self.__data, call=False)
    (2nd option implies 'callback' returns whatever the last attr.__call__ would return)

    """
    def __init__(self, obj, callback, stop_keys=None, initial_data=None):
        self.__data = [initial_data] if initial_data is not None else []
        self.__stop_keys = set(stop_keys) if stop_keys else []
        self.__parent = obj
        self.__cb = callback

    def __getattr__(self, key):
        self.__data.append(key)
        if key in self.__stop_keys:
            return self.__cb(self.__data, call=False)
        return self

    def __call__(self, *v, **kw):
        last_key = self.__data[-1]
        self.__data.append("__call__")
        return self.__cb(self.__data, call=True)(*v, **kw)


