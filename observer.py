#! /usr/bin/python3

# Pretty much lifted from Wikipedia article "Observer pattern"

class Observer:
    def __init__(self, observable):
        observable.register_observer(self)

    def notify(observable, *args, **kwargs):
        '''Override with subclass's implementation'''
        raise NotImplementedError

class Observable:
    '''register observers with this'''
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for o in self._observers:
            o.notify(self, *args, **kwargs)

    def _common_notify(func):
        '''decorator to notify observers after running method'''
        def return_f(*args, **kwargs):
            r = func(*args, **kwargs)
            notify_args = common_args(r)
            self.notify_observers(*notify_args)
            return r
        return return_f

    def _common_args(self, a):
        '''Override this to return what you want to send to observers'''
        raise NotImplementedError
