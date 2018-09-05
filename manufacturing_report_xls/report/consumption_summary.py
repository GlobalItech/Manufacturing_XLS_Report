from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import fields, models,api
from datetime import date, datetime

class McrReportXls(ReportXlsx):
    

    @api.multi
    def get_lines(self, date_from, date_to, product_categ, report_type, location, product, cat, warehouse,mo):
         
        lines = []
        if product:
            product_ids = self.env['product.product'].search([('categ_id','=',cat.id),('id','in',product)])
        else:
            product_ids = self.env['product.product'].search([('categ_id','=',cat.id)])
        array = []
        for lo in location:
            array.append(lo.id)
        for product in product_ids:
            if mo:
                product_data=  self.env['mrp.production'].search([('date_planned_start', '>=',date_from),('date_planned_start', '<=',date_to),('location_dest_id', 'in',array),('product_id', '=',product.id),('state','=','done'),('id','in',mo)])
            else:
                product_data=  self.env['mrp.production'].search([('date_planned_start', '>=',date_from),('date_planned_start', '<=',date_to),('location_dest_id', 'in',array),('product_id', '=',product.id),('state','=','done')])
            
            for prod in product_data:
#                 if 'MO' in prod.name:
#                 flag = True
                number = 1
                for l in prod.move_finished_ids:
            
                    vals = {
                        'code':  l.product_id.default_code or '',
                        'name': l.product_id.name + ' ' + str(l.product_id.attribute_value_ids.name or ''),
                        'production': l.quantity_done or 0,
                        'to_consume': 0,
                        'consumed': 0,
                        'brand':  l.product_id.name or '',
                        'number':number,
                        'mo_number': l.origin,
                        }
                    lines.append(vals)
                    number+=1
                    
                for l in prod.move_raw_ids:
                    vals = {
                        'code':  l.product_id.default_code or '',
                        'name': l.product_id.name + ' ' + str(l.product_id.attribute_value_ids.name or ''),
                        'production':0,
                        'to_consume': l.product_uom_qty or 0,
                        'consumed': l.quantity_done or 0,
                        'brand':  '',
                        'number': number,
                        'mo_number':l.origin
                        }
                    lines.append(vals)
                    number+=1
                number+=1
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
#         if report_name == 'grand_production_summary':
#             sheet.merge_range(0, 0, 0, 2, 'Grand Production Summary ', format11)
        if report_name == 'consumption_summary':
            sheet.merge_range(0, 0, 0, 5, 'Production Receipt and Consumption Summary Report ', format11)
            sheet.merge_range(1, 0, 1, 5, 'Period from: ' + (date_from) +  ' to ' + (date_to), period_format)

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
        if report_name == 'consumption_summary':
            for ware in warehouse:
                
                locations = self.env['stock.location'].search([('Wr_id','=',ware.id)])
                array1 = []
                for lo in locations:
                    array1.append(lo.id)
                product_data2=[]
                if data['form']['mo_ref']:
                    product_data=  self.env['mrp.production'].search([('create_date', '>=',data['form']['date_from']),('create_date', '<=',data['form']['date_to']),('location_dest_id', 'in',array1),('id','in',data['form']['mo_ref']),('state','=','done')])
                    for l in product_data:
                        product_data2.append(l.name)
                else:
                    product_data=  self.env['mrp.production'].search([('create_date', '>=',data['form']['date_from']),('create_date', '<=',data['form']['date_to']),('location_dest_id', 'in',array1)])
                    for l in product_data:
                        product_data2.append(l.name)
                if product_data:
                    sheet.merge_range(product_row-3, 0, product_row-3, 5,ware.name, format12)
                    temp = 0
                    for cat in category:
                        
                        get_lines = self.get_lines(data['form']['date_from'],data['form']['date_to'],category,data['form']['report_type'],locations,data['form']['product'],cat,ware,data['form']['mo_ref'])
                #        
                        
                        totalp = 0
                        totalt = 0
                        totalc = 0
                        
                        if get_lines:
                            sheet.write(product_row-2, 0, 'Category', format12)
                            sheet.merge_range(product_row-2, 1,product_row-2, 2,cat.name, format12)
                            # sheet.merge_range(product_row-2, 3,product_row-2, 5, product_data2[temp] , format12)
                            
                            sheet.write(product_row-1, 0,'Code', format12)
                            sheet.write(product_row-1, 1,'Brand', format12)
                            sheet.write(product_row-1, 2,'Name', format12)
                            sheet.write(product_row-1, 3,'Production (kg)', format12)
                            sheet.write(product_row-1, 4,'Material to Consume', format12)
                            sheet.write(product_row-1, 5,'Material Consumed', format12)

                            
#                             p_name=''
                            flag = True
                            mo_array = []
                            for line in get_lines:

                                mo_number = line['mo_number']
                                if mo_number not in mo_array:
                                    sheet.merge_range(product_row, 0, product_row, 5, line['mo_number'], format12)
#                                     sheet.write(product_row, 0, line['mo_number'], format12)
                                    mo_array.append(mo_number)
                                    product_row +=1
                #             date =datetime.strptime(line['date'],'%Y-%m-%d').strftime('%d-%m-%y')
                #             sheet.write(product_row, 0, date, format_center)

                                sheet.write(product_row, 0, line['code'], format_center)
                                sheet.write(product_row, 1, line['brand'], Pname_format)
                                sheet.write(product_row, 2, line['name'], Pname_format)
                                sheet.write(product_row, 3, line['production'], qty_format)
                                totalp+=line['production']
        #                             sheet.write(product_row, 3, line['description'], Pname_format)
                                sheet.write(product_row, 4, line['to_consume'], qty_format)
                                totalt+=line['to_consume']
                                sheet.write(product_row, 5, line['consumed'], qty_format)
                                totalc+=line['consumed']
                                product_row +=1
                                
#                                 sheet.write(product_row, 2,'Sub Total', format21)
#                                 sheet.write(product_row, 3, totalp, subtotal_format)
#                                 sheet.write(product_row, 4, totalt, subtotal_format)
#                                 sheet.write(product_row, 5, totalc, subtotal_format)
#                                 product_row+=1
#                                 p_name =''
#                             sheet.write(product_row, 2,'Sub Total', format21)
#                             sheet.write(product_row, 3, totalp, subtotal_format)
#                             sheet.write(product_row, 4, totalt, subtotal_format)
#                             sheet.write(product_row, 5, totalc, subtotal_format)
                            product_row+=4
                            temp+=1        
McrReportXls('report.manufacturing_c_report_xls.mcr_xls.xlsx','product.product')
