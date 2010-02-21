
from nevow import page
from nevow import athena
from nevow import loaders
from nevow import tags as T

class TextInput(athena.LiveElement):
    docFactory = loaders.stan(
        T.div(class_="formlet-field")[
            T.label(render="label"),
            T.input(render="input"),
        ])

    def __init__(self, original):
        super(TextInput, self).__init__()
        self.original = original

    @page.renderer
    def label(self, request, tag):
        return tag(for_=self.original.ID)[self.original.label]

    @page.renderer
    def input(self, request, tag):
        return tag(type_=self.original.type_, id=self.original.ID)

