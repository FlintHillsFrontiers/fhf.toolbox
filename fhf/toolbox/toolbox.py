from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from plone import api
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
from fhf.toolbox.drawer import IDrawer

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


class DrawerView(grok.View):
    """ view drawers in filter-able summary"""

    grok.context(IToolbox)
    grok.require('zope2.View')

    def drawers(self):
        """Return a catalog search result of tools to show
        """

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
    
        return context.listFolderContents(contentFilter={ 
                "object_provides" : IDrawer.__identifier__,
                })

    def isContributor(self):
        return api.user.get_permissions(obj=self.context).get('Request review')


class ToolView(grok.View):
    """ view tools in filter-able summary bubbles """

    grok.context(IToolbox)
    grok.require('zope2.View')

    def tools(self):
        """Return a catalog search result of tools to show
        """

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
         
        path = context.getPhysicalPath()
        path = '/'.join(path)
        return catalog.searchResults(
                path={'query': path},
                object_provides=ITool.__identifier__,
                )

class LoadView(grok.View):
    """ loads tools the FHF google spreadsheet """

    grok.context(IToolbox)
    grok.require('zope2.View')

    def expand_audience(self, f):
        if f == '' or f == 'All':
            return [u'Citizen Leader', u'Local Government',
                    u'State Government', u'Federal and Tribal Gov',
                    u'Community Organization',
                    u'Planning and Development Org',
                    u'Educational Organization',
                    u'Property Owner',
                    ]
        else:
            return [unicode(s.strip()) for s in f.split(',')]

    def init_richtext_field(self, f, alt=None):
        """ if the field has content return it as a RichTextValue """
        if f:
            return RichTextValue(unicode(f))
        elif alt:
            return RichTextValue(unicode(alt))
        else:
            return None

    def load_wks(self, wks, issue_area):
        """ load the specified worksheet.

        Iterate over the worksheet by row creating necessary drawers
        and tools.  Currently assumes the following mapping between
        row index and values:
            1 - toolid
            2 - title
            3 - audience
            4 - overview (Description)
            5 - step_1
            6 - step_2
            7 - step_3
            8 - 
            9 - resources
           10 - case_study

        Note: assumes the appropriate drawer is given immediately prior
        to tools.
        """

        #import pdb; pdb.set_trace()

        for row in wks.get_all_values()[2:]:

            # skip rows without tool ID
            if not row[0]:
                continue

            # create drawer when tool ID ends with '.0'
            if row[0].endswith('.0'):
                drawer = createContentInContainer(self.context,
                        'fhf.toolbox.drawer',
                        toolid = unicode(row[0]),
                        title = unicode(row[1]),
                        overview = self.init_richtext_field(row[4], alt=row[1]),
                        issue_area = unicode(issue_area),
                        )
                continue

            # create tool when tool ID ends with '.x'
            print row
            createContentInContainer(drawer, 'fhf.toolbox.tool',
                toolid = unicode(row[0]),
                title = unicode(row[1].strip()),
                issue_area = unicode(issue_area),
                goals = unicode(row[2]),
                audience = self.expand_audience(row[3]),
                overview = self.init_richtext_field(row[4]),
                steps = self.init_richtext_field(u'<p>' + \
                        u'</p><p>'.join(row[5:8])+u'</p>'),
                cs_description = self.init_richtext_field(row[10]),
                )

    def load(self):
        """ Reloads all the tools from the Google Spreadsheet
        """
        import gspread
        #import pdb; pdb.set_trace()

        gc = gspread.login('jeff.terstriep@gmail.com','qfasbwmegcadaujw')
        ss = gc.open('140226.CommunityToolboxSpreadsheet')

        self.load_wks(ss.worksheet('Natural Systems'), 'Natural Systems') 
        self.load_wks(ss.worksheet('Social Systems'), 'Social Systems') 
        self.load_wks(ss.worksheet('Cultural Systems'), 'Cultural Systems') 
        self.load_wks(ss.worksheet('Farm&Ranch'), 'Farming and Ranching') 
        self.load_wks(ss.worksheet('Opportunity'), 'Economic Opportunity') 
        self.load_wks(ss.worksheet('Mobility&Transportation'), 'Mobility and Transportation') 
        self.load_wks(ss.worksheet('Built Environment'), 'Built Environment') 
            
