from odoo import models, fields, api
from reportlab.graphics.shapes import String
import time
from dateutil import relativedelta
import dateutil.relativedelta
import datetime
from datetime import date
from datetime import datetime , timedelta
from odoo.fields import Many2many


class CostReport(models.TransientModel):
    _name = "wizard.mr"
    _description = "Manufacturing Reports"
    
    warehouse = fields.Many2one('stock.warehouse', string='Warehouse')
    mo_ref= fields.Many2many('mrp.production', string='MO Reference')
    product_categ= fields.Many2many('product.category', string="Product Category")
    location = fields.Many2many('stock.location')
    product =fields.Many2many('product.product', string='Product')
    report_type = fields.Selection([('grand_production_summary','Grand Production Summary'),
                                    ('consumption_summary','Production Receipt and Consumption Summary'),
                                    ('grand_production_summary_sd','Grand Production Summary Scheduled Date')],
                                    string='Relative')
    
    date_from = fields.Date('Date From:',default=time.strftime('%Y-%m-01'))
    date_to = fields.Date('Date To:',default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],)
 


    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'product.product'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
            # if context.get('xls_export'):
            #     return {'type': 'ir.actions.report.xml',
            #             'report_name': 'manufacturing_report_xls.mr_xls.xlsx',
            #             'datas': datas,
            #             'name': 'MR'
            #             }
            if context.get('xls_export'):
                if datas['form']['report_type'] == 'grand_production_summary':
                    return {'type': 'ir.actions.report.xml',
                            'report_name': 'manufacturing_report_xls.mr_xls.xlsx',
                            'datas': datas,
                            'name': 'Grand Summary'
                            }
                elif datas['form']['report_type'] == 'consumption_summary':
                    return {'type': 'ir.actions.report.xml',
                            'report_name': 'manufacturing_c_report_xls.mcr_xls.xlsx',
                            'datas': datas,
                            'name': 'Consumption Summary'
                            }
                    
                elif datas['form']['report_type'] == 'grand_production_summary_sd':
                    return {'type': 'ir.actions.report.xml',
                            'report_name': 'manufacturing_sd_report_xls.sd_xls.xlsx',
                            'datas': datas,
                            'name': 'Grand Summary Scheduled Date'
                            }

          