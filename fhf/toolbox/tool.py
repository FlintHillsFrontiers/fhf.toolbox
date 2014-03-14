import json
from datetime import datetime
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

    def vcount(self):
        """Return the number of votes."""

        if self.votes:
            return len(self.votes)
        else:
            return 0

    def audience_all(self):
        """Return CSV of audiences or All if appropriate

        Warning: should be using vocabularies this uses a hard-coded number.
        """

        if len(self.audience) == 8:
            return "All"
        else:
            return ', '.join(self.audience)


    def get_icon(self):
        """Return the issue area icon.

        Ugly hard-coded mapping from issue area to icon URL.
        
        """
        # workaround to include Plone site if necessary
        # this doesn't work, there must be a better way
        if self.getPhysicalPath()[1] == 'fhf':
            site = '/fhf'
        else:
            site = ''

        if self.issue_area == 'Natural Systems':
            return site + '/issue-areas/natural-icon'
        elif self.issue_area == 'Social Systems':
            return site + '/issue-areas/social-icon'
        elif self.issue_area == 'Cultural Systems':
            return site + '/issue-areas/cultural-icon'
        elif self.issue_area == 'Farming and Ranching':
            return site + '/issue-areas/farm-icon'
        elif self.issue_area == 'Mobility and Transportation':
            return site + '/issue-areas/mobility-icon'
        elif self.issue_area == 'Economic Opportunity':
            return site + '/issue-areas/opportunity-icon'
        elif self.issue_area == 'Built Environment':
            return site + '/issue-areas/built-icon'
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

    def all(self):
        return self.context.aq_parent.absolute_url()

    def next(self):
        ids = [b['id'] for b in self.context.aq_parent.getFolderContents()]
        idx = ids.index(self.context.getId())    

        if idx+1 == len(ids):
            return ""
        else:
            return ids[idx+1]

    def urating(self):
        "Return the user's previous rating from a cookie."
        #import pdb; pdb.set_trace()
        ip,v = self.request.cookies.get("tool_rating", "127.0.0.1 0").split()
        return float(v)


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


class RateItView(grok.View):

    """Called by javascript to register user's rating.

    Logs the IP address and rating into the votes field and updates 
    the tools rating.

    Sets cookie to based on the tools path that holds the user's rating.
    """

    grok.context(ITool)
    grok.require('zope2.Public')
    grok.name('rateit')

    def _next_year(self):
        """Return formated time string for one year from today."""

        ny = datetime.fromordinal(datetime.now().toordinal()+365)
        return ny.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _discard_vote(self):
        """Remove previous vote from votes if it exists."""

        urating = self.request.cookies.get("tool_rating", "")
        if urating:
            p_address, p_value = urating.split(' ')
            try:
                self.context.votes.remove((p_address, float(p_value)))
            except ValueError:
                pass


    def _get_ip(self):
        """ Extract the client IP address from the HTTP request
        in a proxy-compatible way.

        @return: IP address as a string or 127.0.0.1 if not available
        """
        if "HTTP_X_FORWARDED_FOR" in self.request.environ:
            # Virtual host
            ip = self.request.environ["HTTP_X_FORWARDED_FOR"]
        elif "HTTP_HOST" in self.request.environ:
            # Non-virtualhost
            ip = self.request.environ["REMOTE_ADDR"]
        else:
            # a default IP address to write to the cookie
            ip = '127.0.0.1'
    
        return ip


    def render(self):

        # not sure how make this the default with current model
        if not self.context.votes:
            self.context.votes = []

        address = self._get_ip()
        value = float(self.request.get('value'))

        # rating selected
        if value > 0.0:
            self._discard_vote()
            self.context.votes.append((address, value))

            self.request.response.setCookie("tool_rating",
                address + ' ' + str(value),
                path='/'.join(self.context.getPhysicalPath()),
                expires=self._next_year())

        # rating canceled
        else:
            self._discard_vote()
            self.request.response.expireCookie("tool_rating",
                path='/'.join(self.context.getPhysicalPath()))

        # re-calculate current rating based on collected votes
        if len(self.context.votes):
            total = sum([t[1] for t in self.context.votes])
            self.context.rating = total / len(self.context.votes)
        else:
            self.context.rating = 0.0

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(dict(rating=self.context.rating, 
            votes=len(self.context.votes)))
