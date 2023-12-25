from pyproxyclass.proxy_class import ProxyClass, PassthroughInvocationHandler

class TestProxyClass():
    
    class Prueba():
        def __init__(self, a):
            self.a = a
            
        def get_a(self):
            return self.a
    
    def test_proxy_class_init(self):
        # Create a proxy class
        prueba = self.Prueba(1)
        proxy_class = ProxyClass.create_proxy_class(self.Prueba, PassthroughInvocationHandler(prueba))
        print(proxy_class)
        assert isinstance(proxy_class, self.Prueba)
        assert proxy_class.get_a() == 1
        assert proxy_class.a == 1