from .wrapper import wrap, unwrap

class GroupBy:
    def __init__(self, gb_obj):
        self._pl = gb_obj
        self._is_wrapped = True

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            _pl = super().__getattribute__("_pl")
            attr = getattr(_pl, name)
            if callable(attr):
                def wrapped(*args, **kwargs):
                    return wrap(attr(*[unwrap(a) for a in args], **{k: unwrap(v) for k, v in kwargs.items()}))
                return wrapped
            return attr
