from django.conf.urls import patterns, url, include
from flapjack import resources

class Api(resources.Base):
    def __init__(self, api_name="v0"):
        # set the api name
        self.api_name = api_name
        self._registry = {}
    
    def register(self, resource):
        # take a class object as a parameter.
        # add the resource to a vector.
        self._registry[resource.name] = resource
        
    def unregister(self,resource_name):
        #delete from vector
        del self._registry[resource_name]
        
    @property
    def urls(self):
        pattern = []
        for resource in self._registry.values():
            pattern += patterns('', url(r'^{}/'.format(self.api_name), include(resource.urls)))
            
        return pattern
         # [str(x) for x in ]
