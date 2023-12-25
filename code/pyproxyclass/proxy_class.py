import typing as t

class InvocationHandler():
            
    def __call__(self, instance: 'ProxyClass', method: str, *args, **kwargs):
        raise NotImplementedError()
    
    def getattr(self, name):
        raise NotImplementedError()
    
    def setattr(self, name, value):
        raise NotImplementedError()
    
    def delattr(self, name):
        raise NotImplementedError()
    
class PassthroughInvocationHandler(InvocationHandler):
    def __init__(self, object: t.Any) -> None:
        super().__init__()
        self._object = object
        
    def invoke_original_method(self, method: str, *args, **kwargs):
        return getattr(self._object, method)(*args, **kwargs)
        
    def __call__(self, instance: 'ProxyClass', method: str, *args, **kwargs):
        return self.invoke_original_method(method, *args, **kwargs)
    
    def getattr(self, name):
        return getattr(self._object, name)
    
    def setattr(self, name, value):
        return setattr(self._object, name, value)
    
    def delattr(self, name):
        return delattr(self._object, name)
        
    @property
    def object(self):
        return self._object
    
    @object.setter
    def object(self, object: t.Any):
        self._object = object

class ClassMethodHandler():
    
    def __init__(self, method: str, invocation_handler: InvocationHandler) -> None:
        self.method = method
        self.invocation_handler = invocation_handler
    
    def __get__(self, instance, owner):
        from functools import partial
        # if isinstance(instance, ProxyClass):
        #     return partial(instance.get_internal_instance, instance)
        return partial(self.invocation_handler.__call__, instance=instance, method=self.method)

class ProxyMetaClass(type):
        def __new__(mcls, classname, bases, classdict, **kwargs):
            invocation_handler = kwargs.get("invocation_handler", InvocationHandler())
            base_type = kwargs["base_object_type"]
            base_dir = dir(base_type)
            for key in base_dir:
                if key.startswith("__") and key.endswith("__"):
                    continue
                if key in classdict:
                    continue
                classdict[key] = ClassMethodHandler(key, invocation_handler)
            wrapped_classname = '_%s_%s' % ('Wrapped', base_type.__name__)
            return super().__new__(mcls, wrapped_classname, bases+(base_type,), classdict)

T = t.TypeVar('T')
class ProxyClass():
    
    def __init__(self, invocation_handler: InvocationHandler) -> None:
        self._invocation_handler = invocation_handler
        
    def __getattr__(self, name):
        if name.startswith("_"):
            return super().__getattr__(name)
        return self._invocation_handler.getattr(name)
    
    def __setattr__(self, name, value):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        return self._invocation_handler.setattr(name, value)
    
    def __delattr__(self, name):
        if name.startswith("_"):
            return super().__delattr__(name)
        return self._invocation_handler.delattr(name)
    
    def get_invocation_handler(self) -> InvocationHandler:
        return self._invocation_handler
    
    @staticmethod
    def create_proxy_class(base_object: t.Type[T], invocation_handler: t.Optional[InvocationHandler])-> T:
        base_object_type = base_object
        if invocation_handler is None:
            invocation_handler = InvocationHandler()
        class SpecificProxyClass(ProxyClass, metaclass=ProxyMetaClass, base_object_type=base_object_type, invocation_handler=invocation_handler):
            pass
        return t.cast(T,SpecificProxyClass(invocation_handler))
    
class WrapperClass(ProxyClass):
    
    def __init__(self, invocation_handler: PassthroughInvocationHandler) -> None:
        self._invocation_handler = invocation_handler
        
    def get_internal_instance(self):
        return self._invocation_handler.object
    
    @staticmethod
    def create_wrapper_class(base_object: T, invocation_handler: t.Optional[PassthroughInvocationHandler])-> T:
        if invocation_handler is None:
            invocation_handler = PassthroughInvocationHandler(base_object)
        while isinstance(base_object, WrapperClass):
            base_object = base_object.get_internal_instance()
        base_object_type = type(base_object)
        class SpecificWrapperClass(WrapperClass, metaclass=ProxyMetaClass, base_object_type=base_object_type, invocation_handler=invocation_handler):
            pass
        return t.cast(T,SpecificWrapperClass(invocation_handler))