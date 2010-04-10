import formal
from formal.examples import main

class DynamicFormPage(main.FormExamplePage):
    
    title = 'Dynamic Form'
    description = 'Building a form dynamically by modifying it.'
    
    def form_example(self, ctx):
        # Create a form
        form = formal.Form()
        form.addField('first', formal.String())
        form.addGroup('group')
        form.addField('last', formal.String())
        # Add new fields at specific places.
        form.addFirst(formal.Field('newFirst', formal.String()))
        form.addLast(formal.Field('newLast', formal.String()))
        form.addBefore(formal.Field('beforeGroup', formal.String()), 'group')
        form.addAfter(formal.Field('afterGroup', formal.String()), 'group')
        form.addLast(formal.Field("one", formal.String()), "group")
        form.addLast(formal.Field("three", formal.String()), "group")
        form.addBefore(formal.Field("two", formal.String()), "group.three")
        return form

    def submitted(self, ctx, form, data):
        print form, data
