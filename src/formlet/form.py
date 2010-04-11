
import os

from nevow import athena
from nevow import page
from nevow import loaders
from nevow import tags as T
from twisted.python.util import sibpath

def tpt(filename):
    return os.path.join(sibpath(__file__, "templates"), filename)

class FormElement(athena.LiveElement):
    docFactory = loaders.xmlfile(tpt("form.html"))
    jsClass = u"Formlet.Form"

    def __init__(self, original):
        super(FormElement, self).__init__()
        self.original = original

    @page.renderer
    def action(self, request, tag):
        return tag(value=self.original.action)

    @page.renderer
    def fields(self, request, tag):
        return tag[(f.element(self) for f in self.original.fields)]

    @page.renderer
    def buttons(self, request, tag):
        return tag[(b.element(self) for b in self.original.buttons)]

    @athena.expose
    def process(self, kw):
        print "++++++++++++++++++++++++ PROCESS"
        # todo - check the method being called is exposed
        action = str(kw.pop('formlet.action'))
        kw = dict((str(a), b) for (a,b) in kw.items() if a)
        getattr(self.fragmentParent, action)(**kw)

class Form(object):

    def __init__(self, name, action):
        self.name = name
        self.action = action
        self.fields = []
        self.buttons = []

    def addField(self, field):
        self.fields.append(field)

    def addButton(self, button):
        self.buttons.append(button)

    def fieldID(self, field):
        return "formlet-%s-%s" % (self.name, field.name)

    def element(self, parent):
        e = FormElement(self)
        e.setFragmentParent(parent)
        return e
