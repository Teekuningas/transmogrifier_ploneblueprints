# -*- coding: utf-8 -*-
from plone import api
from venusianconfiguration import configure
from Acquisition import aq_base

from transmogrifier.blueprints import ConditionalBlueprint
from transmogrifier_ploneblueprints.utils import traverse


@configure.transmogrifier.blueprint.component(name='plone.local_roles.get')
class GetLocalRoles(ConditionalBlueprint):
    def __iter__(self):
        for item in self.previous:
            if self.condition(item):
                ob = item['_object']
                item['_block_inherit'] = getattr(aq_base(ob),
                                                 '__ac_local_roles_block__',
                                                 False)
                item['_local_roles'] = getattr(aq_base(ob),
                                               '__ac_local_roles__', {})
            yield item


@configure.transmogrifier.blueprint.component(name='plone.local_roles.set')
class SetLocalRoles(ConditionalBlueprint):
    def __iter__(self):
        portal = api.portal.get()
        for item in self.previous:
            if self.condition(item):
                ob = traverse(portal, item['_path'])
                ob.__ac_local_roles__ = item['_local_roles']
                ob.__ac_local_roles_block__ = item['_block_inherit']
            yield item
