#! /usr/bin/python3

# Pretty much lifted from Wikipedia article "Observer pattern"

class Observer:
    def __init__(self, observable):
        observable.register_observer(self)

    def notify(observable, *args, **kwargs):
        '''Override with subclass's implementation'''
        pass

class Observable:
    '''register observers with this'''
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for o in self._observers:
            o.notify(self, *args, **kwargs)

