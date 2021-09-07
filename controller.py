#! /usr/bin/python3

from observer import Observer

class Controller(Observer):
    '''The superclass of all Controllers for the train sim. You'll need to 
    add your own view-controller interface things'''

    def __init__(self, model, view_class, parent_frame):
        self._model = model
        self._view = view_class(self, parent_frame)
        self._update_view()
        # do this last since modifying (registering with) model shouldn't
        # happen until all else has been successful
        super().__init__(self._model)

    def notify(self, observable, message, arg=None):
        if message not in ("ChangeSuccess", "ChangeFail", "NoChange"):
            raise ValueError("Message "+str(message)+" is not known")

        if observable is self._model:
            if message == "ChangeSuccess":
                print("Change success")
                self._update_view()
            elif message == "ChangeFail":
                # arg should be an exception
                print("Error: "+type(arg).__name__+str(arg.args))
                # update view anyway (easiest way to set correct view)
                self._update_view()
            elif message == "NoChange":
                print("No change")
            else:
                # shouldn't get here
                raise RuntimeError("should not get here (message and arg: "\
                        "'{}'; '{}')".format(message, arg))
        else:
            raise ValueError("{} is not the model ({})".format(observable,
                self._model))

    def _update_view(self):
        raise NotImplementedError("override this method in subclasses")
