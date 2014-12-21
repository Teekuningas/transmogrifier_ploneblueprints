# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from venusianconfiguration import configure
from transmogrifier.blueprints import ConditionalBlueprint
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IMutableUUID

import pkg_resources

try:
    pkg_resources.get_distribution('Products.Archetypes')
except pkg_resources.DistributionNotFound:
    HAS_ARCHETYPES = False
else:
    from Products.Archetypes import interfaces as AT
    from Products.Archetypes.config import UUID_ATTR
    HAS_ARCHETYPES = True

try:
    pkg_resources.get_distribution('plone.app.referenceablebehavior')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY_REFERENCEABLE = False
else:
    from plone.app.referenceablebehavior import interfaces as DX
    HAS_DEXTERITY_REFERENCEABLE = True


@configure.transmogrifier.blueprint.component(name='plone.get_uuid')
class GetUUID(ConditionalBlueprint):
    def __iter__(self):
        object_key = self.options.get('object-key', '_object')
        for item in self.previous:
            if self.condition(item) and object_key in item:
                uuid = IUUID(item.get(object_key), None)
                if uuid is not None:
                    item['_uuid'] = uuid
            yield item


# noinspection PyProtectedMember
def set_uuid(ob, uuid):
    types_tool = api.portal.get_tool('portal_types')
    fti = types_tool.get(ob.portal_type)
    if IDexterityFTI.providedBy(fti):
        # DX
        if HAS_DEXTERITY_REFERENCEABLE:
            if DX.IReferenceable.provdedBy(ob):
                ob._uncatalogUID(api.portal.get())
        # noinspection PyArgumentList
        IMutableUUID(ob).set(str(uuid))
        if HAS_DEXTERITY_REFERENCEABLE:
            if DX.IReferenceable.provdedBy(ob):
                ob._catalogUID(api.portal.get())
    elif HAS_ARCHETYPES:
        if AT.IReferenceable.providedBy(ob):
            # AT
            ob._uncatalogUID()
            ob._setUID(uuid)


@configure.transmogrifier.blueprint.component(name='plone.set_uuid')
class SetUUID(ConditionalBlueprint):
    def __iter__(self):
        object_key = self.options.get('object-key', '_object')
        for item in self.previous:
            if self.condition(item) and object_key in item:
                set_uuid(item.get(object_key))
            yield item
