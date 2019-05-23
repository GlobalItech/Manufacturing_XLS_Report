from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import fields, models,api
from datetime import date, datetime

class WcrReportXls(ReportXlsx):
    

    @api.multi
    def get_lines(self, date_from,  report_type, location, product, warehouse,mo):
         
        lines=[]
        array = []
        for lo in location:
            array.append(lo.id)
            if mo:
                product_data=  self.env['mrp.production'].search([('date_planned_start', '<=',date_from),('location_dest_id', 'in',array),('state','=','progress'),('id','in',mo)])
            else:
                product_data=  self.env['mrp.production'].search([('date_planned_start', '<=',date_from),('location_dest_id', 'in',array),('state','=','progress')])
            
            for prod in product_data:
                for l in prod.workorder_ids:
                    if(l.state == 'progress'):
                        number = 1
                        vals = {
                            'code':  prod.product_id.default_code or '',
                            'name': prod.product_id.name + ' ' + str(prod.product_id.attribute_value_ids.name or ''),
                            'production': l.qty_producing,
                            'work_center':l.workcenter_id.name,
                            'number':number,
                            'mo_number': prod.name,
                            }
                        lines.append(vals)
                        number+=1
        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('a')
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
        font_size_8.set_align('center')
        justify.set_align('justify')
        format1.set_align('center') 
        red_mark.set_align('center')
                
        date_from = datetime.strptime(data['form']['date_from'], '%Y-%m-%d').strftime('%d/%m/%y')
        if report_name == 'work_centers_wise':
            sheet.merge_range(0, 0, 0, 5, 'Lahore Apparel ', format11)
            sheet.merge_range(1, 0, 1, 5, 'Manufacturing Orders in Process Report ', format11)
            sheet.merge_range(2, 0, 2, 5, 'As on: ' + (date_from), period_format)

        product_row = 6
        cat_row = 2
        warehouse = data['form']['warehouse']
        if warehouse:
            warehouse = warehouse[0]
            locations = data['form']['location']
            warehouse = self.env['stock.warehouse'].search([('id','=',warehouse)])
        else:
            warehouse = self.env['stock.warehouse'].search([])
        if report_name == 'work_centers_wise':
            for ware in warehouse:
                
                locations = self.env['stock.location'].search([('Wr_id','=',ware.id)])
                array1 = []
                for lo in locations:
                    array1.append(lo.id)
                product_data2=[]
                if data['form']['mo_ref1']:
                    product_data=  self.env['mrp.production'].search([('date_planned_start', '<=',data['form']['date_from']),('location_dest_id', 'in',array1),('id','in',data['form']['mo_ref1']),('state','=','progress')])
                else:
                    product_data=  self.env['mrp.production'].search([('date_planned_start', '<=',data['form']['date_from']),('location_dest_id', 'in',array1),('state','=','progress')])
                if product_data:
                    sheet.merge_range(product_row-3, 0, product_row-3, 3,ware.name+"(WH)", format12)
                    temp = 0
                        
                    get_lines = self.get_lines(data['form']['date_from'],data['form']['report_type'],locations,data['form']['product'],ware,data['form']['mo_ref1'])
                        

                        
                    if get_lines:
                            
                            sheet.write(product_row-1, 0,'Code', format12)
                            sheet.write(product_row-1, 1,'Name', format12)
                            sheet.write(product_row-1, 2,'Production', format12)
                            sheet.write(product_row-1, 3,'Work Centers', format12)

                            flag = True
                            mo_array = []
                            for line in get_lines:
                                mo_number = line['mo_number']
                                if mo_number not in mo_array:
                                    sheet.merge_range(product_row, 0, product_row, 3, line['mo_number'], format12)
#                                     sheet.write(product_row, 0, line['mo_number'], format12)
                                    mo_array.append(mo_number)
                                    product_row +=1
                                sheet.write(product_row, 0, line['code'], format_center)
#                                 sheet.write(product_row, 1, line['brand'], Pname_format)
                                sheet.write(product_row, 1, line['name'], Pname_format)
                                sheet.write(product_row, 2, line['production'], qty_format)
                                sheet.write(product_row, 3, line['work_center'], qty_format)
                                product_row +=1
                                
                            product_row+=4
                            temp+=1        
WcrReportXls('report.manufacturing_w_report_xls.work_xls.xlsx','product.product')
