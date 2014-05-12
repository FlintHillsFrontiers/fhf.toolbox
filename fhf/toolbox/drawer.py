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

class IDrawer(form.Schema, IImageScaleTraversable):
    """
    A folder for collecting the "tools" into "drawers".
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/toolbox.xml to define the content type.

    form.model("models/drawer.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Drawer(Container):
    grok.implements(IDrawer)

    icons = {
        'Natural Systems': '++resource++fhf.toolbox/natural.png',
        'Social Systems': '++resource++fhf.toolbox/social.png',
        'Cultural Systems': '++resource++fhf.toolbox/cultural.png',
        'Farming and Ranching': '++resource++fhf.toolbox/farm.png',
        'Mobility and Transportation': '++resource++fhf.toolbox/mobility.png',
        'Economic Opportunity': '++resource++fhf.toolbox/opportunity.png',
        'Built Environment': '++resource++fhf.toolbox/built.png',
        }


    def get_tools(self):
        """Return a catalog search result of tools to show
        """

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
    
        return catalog(object_provides=ITool.__identifier__,
                       path='/'.join(context.getPhysicalPath()),
                       sort_on='sortable_title')


    def get_icon(self):
        """Return the issue area icon.

        Returns the IA icon from the resource directory based on the
        IA title.
        """

        return self.icons.get(self.issue_area, '')


class ShortView(grok.View):
    """ summary view normally designed for listings """

    grok.context(IDrawer)
    grok.require('zope2.View')

    bubbleTemplate = grok.PageTemplateFile("drawer_templates/bubbleview.pt")

    def tools(self):
        """Return a catalog search result of tools to show
        """

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return context.listFolderContents(contentFilter={
                       "object_provides" : ITool.__identifier__,
                       })

    def shortDesc(self, description):
        """ truncate description to 100 words """
    
        d = description.split()
        if len(d) > 100:
           description = ' '.join(d[:100]) + '...'

        return description


    def renderBubble(self):
        return self.bubbleTemplate.render(self)


