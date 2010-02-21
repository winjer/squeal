
from nevow import page
from nevow import athena
from nevow import loaders
from nevow import tags as T

class Element(athena.LiveElement):
    def __init__(self, original):
        super(Element, self).__init__()
        self.original = original

class Button(Element):
    docFactory = loaders.stan(
        T.button(render="button"))

    @page.renderer
    def button(self, request, tag):
        return tag(type_=self.original.type_)[self.original.label]

class SimpleInput(Element):
    docFactory = loaders.stan(T.input(render="input"))

    @page.renderer
    def input(self, request, tag):
        tag = tag(type_=self.original.type_,
                  id=self.original.ID,
                  name=self.original.name)
        if self.original.value is not None:
            tag = tag(value=self.original.value)
        return tag

class TextInput(SimpleInput):
    docFactory = loaders.stan(
        T.div(class_="formlet-field")[
            T.label(render="label"),
            T.input(render="input"),
        ])

    @page.renderer
    def label(self, request, tag):
        return tag(for_=self.original.ID)[self.original.label]

