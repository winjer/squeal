
import widget

class Field(object):

    def __init__(self, form, name, **kw):
        self.name = name
        form.addField(self)
        self.ID = form.fieldID(self)
        self.widget = kw.get("widget", widget.TextInput)
        self.label = kw.get("label", "unlabelled")

    def element(self, parent):
        w = self.widget(self)
        w.setFragmentParent(parent)
        return w

class StringField(Field):

    def __init__(self, **kw):
        self.type_ = kw.get("type", "text")
        super(StringField, self).__init__(**kw)
