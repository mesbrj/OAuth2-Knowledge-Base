import inspect

from core.use_cases import dataManagerImpl, publicCrud

def inbound_factory(type=str):
    if type == "data":
        caller_frame = inspect.stack()[1]
        module = inspect.getmodule(caller_frame[0])
        if "adapter.rest" in module.__name__:
            return publicCrud()
        else:
            return dataManagerImpl()

    if type == "service":
        pass