import pkg_resources
from zope.interface import implements
from twisted.python import reflect
from nevow import appserver, inevow, loaders, rend, static, tags as T, url
import formal

DOCTYPE = T.xml('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
CHARSET = T.xml('<meta http-equiv="content-type" content="text/html; charset=utf-8" />')

examples = [
    'formal.examples.simple.SimpleFormPage',
    'formal.examples.types.TypesFormPage',
    'formal.examples.required.RequiredFormPage',
    'formal.examples.missing.MissingFormPage',
    'formal.examples.prepopulate.PrepopulateFormPage',
    'formal.examples.group.GroupFormPage',
    'formal.examples.stanstyle.StanStyleFormPage',
    'formal.examples.fileupload.FileUploadFormPage',
    'formal.examples.smartupload.SmartUploadFormPage',
    'formal.examples.selections.SelectionFormPage',
    'formal.examples.datestimes.DatesTimesFormPage',
    'formal.examples.actionbuttons.ActionButtonsPage',
    'formal.examples.validator.ValidatorFormPage',
    'formal.examples.restwidget.ReSTWidgetFormPage',
    'formal.examples.nofields.NoFieldsFormPage',
    'formal.examples.hidden.HiddenFieldsFormPage',
    'formal.examples.textareawithselect.TextAreaWithSelectFormPage',
    'formal.examples.richtextarea.RichTextAreaFormPage',
    'formal.examples.sequences.SequencesFormPage',
    'formal.examples.dynamic.DynamicFormPage',
    ]

def makeSite():
    root = RootPage()
    site = appserver.NevowSite(root, logPath="web.log")
    return site

class RootPage(rend.Page):
    """
    Main page that lists the examples and makes the example page a child
    resource.
    """

    docFactory = loaders.stan(
        T.invisible[
            DOCTYPE,
            T.html[
                T.head[
                    CHARSET,
                    T.title['Forms Examples'],
                    T.link(rel='stylesheet', type='text/css', href=url.root.child('examples.css')),
                    ],
                T.body[
                    T.directive('examples'),
                    ],
                ],
            ],
        )

    def render_examples(self, ctx, data):
        for name in examples:
            cls = reflect.namedAny(name)
            yield T.div(class_='example')[
                T.h1[T.a(href=url.here.child(name))[cls.title]],
                T.p[cls.description],
                ]

    def childFactory(self, ctx, name):
        if name in examples:
            cls = reflect.namedAny(name)
            return cls()


class FormExamplePage(formal.ResourceMixin, rend.Page):
    """
    A base page for the actual examples. The page renders something sensible,
    including the title example and description. It also include the "example"
    form in an appropriate place.
    
    Each example page is expected to provide the title and description
    attributes as well as a form_example method that builds and returns a
    formal.Form instance.
    """
    docFactory = loaders.stan(
        T.invisible[
            DOCTYPE,
            T.html[
                T.head[
                    CHARSET,
                    T.title(data=T.directive('title'), render=rend.data),
                    T.link(rel='stylesheet', type='text/css', href=url.root.child('examples.css')),
                    T.link(rel='stylesheet', type='text/css', href=url.root.child('formal.css')),
                    T.script(type='text/javascript', src='js/formal.js'),
                    ],
                T.body[
                    T.h1(data=T.directive('title'), render=rend.data),
                    T.p(data=T.directive('description'), render=rend.data),
                    T.directive('form example'),
                    ],
                ],
            ],
        )

    def data_title(self, ctx, data):
        return self.title

    def data_description(self, ctx, data):
        return self.description


# Add child_ attributes
examples_css = pkg_resources.resource_filename('formal.examples', 'examples.css')
setattr(RootPage, 'child_examples.css', static.File(examples_css))
setattr(RootPage, 'child_formal.css', formal.defaultCSS)
setattr(RootPage, 'child_js', formal.formsJS)

if __name__ == '__main__':
    
    import sys
    from twisted.internet import reactor
    from twisted.python import log
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8000
    
    log.startLogging(sys.stdout)
    site = makeSite()
    reactor.listenTCP(port, site)
    reactor.run()
    
