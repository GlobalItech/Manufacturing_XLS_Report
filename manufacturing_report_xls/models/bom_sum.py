from odoo import models, fields, api
from pygments.lexer import _inherit


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit= 'mrp.production'
class Mrpbom(models.Model):
    _inherit= 'mrp.bom'
