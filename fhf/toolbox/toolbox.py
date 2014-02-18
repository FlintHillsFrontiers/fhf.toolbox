from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from plone.dexterity.content import Container
from plone.dexterity.utils import createContentInContainer
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from fhf.toolbox.tool import ITool

from fhf.toolbox import MessageFactory as _


# Interface class; used to define content-type schema.

class IToolbox(form.Schema, IImageScaleTraversable):
    """
    A folder for managing the "tools" from the Community Toolbox.
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/toolbox.xml to define the content type.

    form.model("models/toolbox.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Toolbox(Container):
    grok.implements(IToolbox)

    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# toolbox_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.
class SampleView(grok.View):
    """ view tools in filter-able summary bubbles """

    grok.context(IToolbox)
    grok.require('zope2.View')

    def tools(self):
        """Return a catalog search result of tools to show
        """

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
    
        return catalog(object_provides=ITool.__identifier__,
                       path='/'.join(context.getPhysicalPath()),
                       sort_on='sortable_title')
    

class BubbleView(grok.View):
    """ view tools in filter-able summary bubbles """

    grok.context(IToolbox)
    grok.require('zope2.View')

    def tools(self):
        """Return a catalog search result of tools to show
        """

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
    
        return context.listFolderContents(contentFilter={
                       "object_provides" : ITool.__identifier__,
                       })
    

class LoadView(grok.View):
    """ loads tools the FHF google spreadsheet """

    grok.context(IToolbox)
    grok.require('zope2.View')

    def load_wks(self, wks, issue_area):
        for rec in wks.get_all_values()[2:]:

            # skip empty description lines
            if rec[3] == '':
                continue

            # cleanup audience so All and empty map to all audiences
            if rec[2] == '' or rec[2] == 'All':
                audience = [u'Citizen Leader', u'Local Government',
                            u'State Government', u'Federal and Tribal Gov',
                            u'Community Organization',
                            u'Planning and Development Org',
                            u'Educational Organization',
                            u'Property Owner',
                            ]
            else:
                audience = [unicode(s.strip()) for s in rec[2].split(',')]

            createContentInContainer(self.context, 'fhf.toolbox.tool',
                title = unicode(rec[0]),
                issue_area = unicode(issue_area),
                goals = unicode(rec[1]),
                audience = audience,
                overview = RichTextValue(unicode(rec[3])),
                step_1 = RichTextValue(unicode(rec[4])),
                step_2 = RichTextValue(unicode(rec[5])),
                step_3 = RichTextValue(unicode(rec[6])),
                resouces = unicode(rec[7]),
                case_study = RichTextValue(unicode(rec[8])),
                )


    def load(self):
        """ Reloads all the tools from the Google Spreadsheet
        """
        import gspread
        #import pdb; pdb.set_trace()

        gc = gspread.login('jeff.terstriep@gmail.com','qfasbwmegcadaujw')
        ss = gc.open('130905.CommunityToolboxSpreadsheet')

        self.load_wks(ss.worksheet('Natural Systems'), 'Natural Systems') 
        self.load_wks(ss.worksheet('Social Systems'), 'Social Systems') 
        self.load_wks(ss.worksheet('Cultural Systems'), 'Cultural Systems') 
        self.load_wks(ss.worksheet('Farm&Ranch'), 'Farming and Ranching') 
        self.load_wks(ss.worksheet('Opportunity'), 'Economic Opportunity') 
        self.load_wks(ss.worksheet('Mobility&Transportation'), 'Mobility and Transportation') 
        self.load_wks(ss.worksheet('Built Environment'), 'Built Environment') 
            
