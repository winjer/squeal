import formal
from formal.examples import main

class SequencesFormPage(main.FormExamplePage):
    
    title = 'Sequences Form'
    description = 'Example of using sequences.'
    
    def form_example(self, ctx):
        form = formal.Form()
        # A list of strings.
        form.addField('strings', formal.Sequence(formal.String()))
        # Required list of strings, where each string is stripped.
        form.addField('requiredAndStripped', formal.Sequence(formal.String(strip=True), required=True))
        # List of strings with max number of items.
        form.addField('maxStrings', formal.Sequence(formal.String(), validators=[formal.LengthValidator(max=3, unit=u"lines")]))
        # A list of integers.
        form.addField('integers', formal.Sequence(formal.Integer()))
        # A list of dates.
        form.addField('dates', formal.Sequence(formal.Date()))
        # A list of tuples
        form.addField('tuples', formal.Sequence(formal.Tuple(fields=[formal.String(), formal.String()])))
        form.addAction(self.submitted)
        return form

    def submitted(self, ctx, form, data):
        print form, data

