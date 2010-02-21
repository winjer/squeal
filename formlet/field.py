
import widget

class Field(object):

    def __init__(self, form, name, **kw):
        self.name = name
        form.addField(self)
        self.ID = form.fieldID(self)
        self.label = kw.get("label", name)
        self.value = kw.get("value", None)

    def element(self, parent):
        w = self.widget(self)
        w.setFragmentParent(parent)
        return w

class StringField(Field):

    def __init__(self, **kw):
        self.widget = kw.get("widget", widget.TextInput)
        self.type_ = kw.get("type_", "text")
        super(StringField, self).__init__(**kw)

class HiddenField(Field):

    def __init__(self, **kw):
        self.widget = kw.get("widget", widget.SimpleInput)
        self.type_ = kw.get("type_", "hidden")
        super(HiddenField, self).__init__(**kw)

class Button(object):

    type_ = "button"

    def __init__(self, form, name, **kw):
        self.name = name
        form.addButton(self)
        self.ID = form.fieldID(self)
        self.widget = kw.get("widget", widget.Button)
        self.label = kw.get("label", name)

    def element(self, parent):
        w = self.widget(self)
        w.setFragmentParent(parent)
        return w

class SubmitButton(Button):

    type_ = "submit"
