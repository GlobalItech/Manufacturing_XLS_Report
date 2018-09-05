from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import fields, models,api
from datetime import date, datetime

class MrReportXls(ReportXlsx):
    

    @api.multi
    def get_lines(self, date_from, date_to, product_categ, report_type, location, product, cat, warehouse):
         
        lines = []
        imf=[]
        if product:
            product_ids = self.env['product.product'].search([('categ_id','=',cat.id),('id','in',product)])
        else:
            product_ids = self.env['product.product'].search([('categ_id','=',cat.id)])
        array = []
        for lo in location:
            array.append(lo.id)
        for product in product_ids:
            product_data=  self.env['stock.move'].search([('create_date', '>=',date_from),('create_date', '<=',date_to),('location_dest_id', 'in',array),('product_id', '=',product.id),('state','=','done')])
            for prod in product_data:
                if 'MO' in prod.name:
                    vals = {
                            'code': prod.product_id.default_code or ' ',
                            'name': prod.product_id.name + ' ' + str(prod.product_id.attribute_value_ids.name or ' '),
                            'production':prod.quantity_done or 0,
                            'description': prod.name,
#                                 'category': cat.name or ' ',
                            }
                    lines.append(vals)
        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet()
        report_name = data['form']['report_type']
        
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center', 'bold': True})
        format11 = workbook.add_format({'font_size': 14, 'align': 'center', 'bold': True,})
#         format123 = workbook.set_column('A:A', 100)
        period_format= workbook.add_format({'font_size': 11, 'align': 'center', 'bold': True})

        format12 = workbook.add_format({'font_size': 11, 'align': 'center', 'bold': True,'right': True, 'left': True,'bottom': True, 'top': True})
        format21 = workbook.add_format({'font_size': 10, 'bold': True, 'align': 'right', 'right': True, 'left': True,'bottom': True, 'top': True})
        format21.set_num_format('#,##0.00')
        qty_format = workbook.add_format({'font_size': 10, 'align': 'right', 'right': True, 'left': True,'bottom': True, 'top': True})
        qty_format.set_num_format('#,##0.00')
        Pname_format = workbook.add_format({'font_size': 10, 'align': 'left', 'right': True, 'left': True,'bottom': True, 'top': True})
        format_center = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True})
        subtotal_format = workbook.add_format({'font_size': 10, 'bold': True, 'align': 'right', 'right': True, 'left': True,'bottom': True, 'top': True})
        subtotal_format.set_num_format('#,##0.00')
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8})
        red_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8,
                                        'bg_color': 'red'})
        justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12})
#         style = workbook.add_format('align: wrap yes; borders: top thin, bottom thin, left thin, right thin;')
#         style.num_format_str = '#,##0.00'
#         format3.set_align('center')
        font_size_8.set_align('center')
        justify.set_align('justify')
        format1.set_align('center') 
        red_mark.set_align('center')
                
        date_from = datetime.strptime(data['form']['date_from'], '%Y-%m-%d').strftime('%d/%m/%y')
        date_to = datetime.strptime(data['form']['date_to'], '%Y-%m-%d').strftime('%d/%m/%y')
        if report_name == 'grand_production_summary':
            sheet.merge_range(0, 0, 0, 2, 'Grand Production Summary ', format11)
            sheet.merge_range(1, 0, 1, 2, 'Period from: ' + (date_from) +  ' to ' + (date_to), period_format)
         
        # report start
        product_row = 5
        cat_row = 2
        warehouse = data['form']['warehouse']
        category = self.env['product.category'].search([])
        product_categ = data['form']['product_categ']
        if product_categ:
            category = self.env['product.category'].search([('id','in',product_categ)])
        else:
            category = self.env['product.category'].search([])
        if warehouse:
            warehouse = warehouse[0]
            locations = data['form']['location']
            warehouse = self.env['stock.warehouse'].search([('id','=',warehouse)])   
        else:
            warehouse = self.env['stock.warehouse'].search([])
        if report_name == 'grand_production_summary':
            for ware in warehouse:
                if data['form']['location']:
                    locations = self.env['stock.location'].search([('id', 'in', data['form']['location'])])
                else:
                    locations = self.env['stock.location'].search([('Wr_id', '=', ware.id)])
                array1 = []
                for lo in locations:
                    array1.append(lo.id)
                product_data=  self.env['mrp.production'].search([('create_date', '>=',data['form']['date_from']),('create_date', '<=',data['form']['date_to']),('location_dest_id', 'in',array1)])
                if product_data:
                    sheet.merge_range(product_row-3, 0, product_row-3, 2,ware.name, format12)
                
                    for cat in category:
                        
                        get_lines = self.get_lines(data['form']['date_from'],data['form']['date_to'],category,data['form']['report_type'],locations,data['form']['product'],cat,ware)
                #        
                #         
                        total = 0
                        total1=0
                        if get_lines:
                            sheet.write(product_row-2, 0, 'Category', format12)
                            sheet.merge_range(product_row-2, 1,product_row-2, 2,cat.name, format12)
                            
                            sheet.write(product_row-1, 0,'Code', format12)
                            sheet.write(product_row-1, 1,'Name', format12)
                            sheet.write(product_row-1, 2,'Production (kg)', format12)
                            
                            temp_code='None'
                            product_code = []
                            for line in get_lines:
                                
                                
                                if temp_code != line['code']:
                                    for pro_line in get_lines:
                                        if pro_line['code'] == line['code']:
                                            total1+=pro_line['production']
                                    sheet.write(product_row, 0, line['code'], format_center)
                                    sheet.write(product_row, 1, line['name'], Pname_format)
                                    sheet.write(product_row, 2, total1, qty_format)
                                    product_row +=1
                                         
                                    total1=0    
                                total+=line['production']
                                temp_code= line['code']
                                
                            sheet.write(product_row, 1,'Sub Total', format21)
                            sheet.write(product_row, 2, total, subtotal_format)
                            product_row+=4
MrReportXls('report.manufacturing_report_xls.mr_xls.xlsx','product.product')
