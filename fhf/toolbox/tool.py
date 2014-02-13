from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from plone.dexterity.content import Item
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder


from fhf.toolbox import MessageFactory as _


# Interface class; used to define content-type schema.

class ITool(form.Schema, IImageScaleTraversable):
    """
    A solution, strategy, policy, or tool developed for the Community Toolbox.
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/tool.xml to define the content type.

    form.model("models/tool.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Tool(Item):
    grok.implements(ITool)

    def check_rating(self, val):
        "simple mechanism for setting checked in the rating system"
        if self.rating == val:
            return "checked"
        else:
            return ""

    def user_rating(self, val):
        "simple mechanism for setting checked in the rating system"
        if self.rating == val:
            return "checked"
        else:
            return ""

    def get_icon(self):
        if self.issue_area == 'Natural Systems':
            return '/fhf/issue-areas/natural-icon'
        elif self.issue_area == 'Social Systems':
            return '/fhf/issue-areas/social-icon'
        elif self.issue_area == 'Cultural Systems':
            return '/fhf/issue-areas/cultural-icon'
        elif self.issue_area == 'Farming and Ranching':
            return '/fhf/issue-areas/farm-icon'
        elif self.issue_area == 'Mobility and Transportation':
            return '/fhf/issue-areas/mobility-icon'
        elif self.issue_area == 'Economic Opportunity':
            return '/fhf/issue-areas/opportunity-icon'
        elif self.issue_area == 'Built Environment':
            return '/fhf/issue-areas/built-icon'
        else:
            return ''



# View class
# The view will automatically use a similarly named template in
# tool_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class ToolView(grok.View):
    """ sample view class """

    grok.context(ITool)
    grok.require('zope2.View')

    def prev(self):
        ids = [b['id'] for b in self.context.aq_parent.getFolderContents()]
        idx = ids.index(self.context.getId())    

        if idx == 0: 
            return ""
        else:
            return ids[idx-1]

    def next(self):
        ids = [b['id'] for b in self.context.aq_parent.getFolderContents()]
        idx = ids.index(self.context.getId())    

        if idx+1 == len(ids):
            return ""
        else:
            return ids[idx+1]


class ShortView(grok.View):
    """ sample view class """

    grok.context(ITool)
    grok.require('zope2.View')

    bubbleTemplate = grok.PageTemplateFile("tool_templates/bubbleview.pt")

    def shortDesc(self, description):
        d = description.split()
        if len(d) > 100:
            description = ' '.join(d[:100]) + '...'

        return description
            

    def renderBubble(self):
        return self.bubbleTemplate.render(self)

