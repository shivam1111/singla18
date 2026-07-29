from odoo import models, fields, api

class MillProductionReport(models.AbstractModel):
    _name = 'report.mill_core.mill_production_report'  # report_name in xml
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Mill Production Report'

    summary_headers = ['', 'Water', 'Solar1 (KW) ', 'Solar2 (KW)', 'Solar1 (KV)', 'Solar2 (KV)', 'KW', 'KV']
    def generate_xlsx_report(self, workbook, data, pos):
        headers_row = ['Size','Qty','Scrap','Scrap %']
        summary_headers = ['','Water','Solar1 (KW) ','Solar2 (KW)','Solar1 (KV)','Solar2 (KV)','KW','KV']
        if len(pos) <= 1:
            report_name = pos[0].name
        else:
            report_name = "Production"
        sheet = workbook.add_worksheet(report_name[:31])
        row_counter = 1 # This is a universal row Counter
        for po in pos:
            def write_row(sheet,column,counter,row,format):
                sheet.write_row('{column}{row}'.format(column=column,row=counter),row,format)
                return counter+1
            header_format = workbook.add_format({'bold': True})
            header_format.set_border()
            header_format.set_align('center')
            date_format = workbook.add_format({'num_format': 'dd/mm/yy','bold':True,'border':1})
            date_format.set_align('center')
            date_row = ['Date',po.date]
            col_counter = len(headers_row)
            row_counter = write_row(sheet,'A',row_counter,date_row,date_format)
            header_row_index = row_counter  # This is a reference for each Production Order Header
            row_counter  = write_row(sheet,'A',row_counter,headers_row+summary_headers,header_format)
            for i,line in enumerate(po.production_line_ids):
                row_format = workbook.add_format()
                row_format.set_align('center')
                row_format.set_border()
                row = [
                       line.size_id.name,line.qty,
                       line.scrap,
                       line.scrap_percentage,
                   ]
                sheet.write_row('A%s' % row_counter, row,row_format)
                row_counter+=1

            col_header_format = workbook.add_format({'bold': True,'border':1})
            col_format = workbook.add_format({'border':1})
            # #Adding Water Column
            sheet.write_column(header_row_index,col_counter,['Op.','Cl.','Net'],col_header_format)
            col_counter+=1
            col_format.set_bold(False)
            sheet.write_column(header_row_index,col_counter,[po.water_units_opening,po.water_units_closing,(po.water_units_closing-po.water_units_opening)],col_format)
            col_counter+=1
            sheet.write_column(header_row_index, col_counter, [po.solar_units_opening_kwh,po.solar_units_closing_kwh],col_format)
            col_counter += 1
            sheet.write_column(header_row_index, col_counter, [po.solar_units_opening_kwh_2,po.solar_units_closing_kwh_2],col_format)
            col_counter += 1
            # Create a format to use in the merged range.
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                }
            )
            sheet.merge_range(f"G{header_row_index+3}:H{header_row_index+3}",po.solar_net,merge_format)
            sheet.write_column(header_row_index, col_counter, [po.solar_units_opening_kvah, po.solar_units_closing_kvah,
                                                              (po.solar_units_closing_kvah - po.solar_units_opening_kvah)],col_format)
            col_counter += 1
            sheet.write_column(header_row_index, col_counter, [po.solar_units_opening_kvah_2, po.solar_units_closing_kvah_2,
                                                              (po.solar_units_closing_kvah_2 - po.solar_units_opening_kvah_2)],col_format)
            col_counter += 1
            kv_solar_net = (po.solar_units_closing_kvah - po.solar_units_opening_kvah)+(po.solar_units_closing_kvah_2 - po.solar_units_opening_kvah_2)*80
            sheet.merge_range(f"I{header_row_index+3}:J{header_row_index+3}", (kv_solar_net), merge_format)
            sheet.write_column(header_row_index, col_counter, [po.kwh_opening, po.kwh_closing,
                                                              (po.kwh_closing - po.kwh_opening)],col_format)

            col_counter += 1
            sheet.write_column(header_row_index, col_counter, [po.kva_opening, po.kva_closing,
                                                              (po.kva_closing - po.kva_opening)],col_format)

            summary_row_index = max(row_counter,header_row_index+4)
            # Summary Printing
            summary_row = ['Total Prod.',po.total_production,'Coal',po.coal,'MD/MT',po.md_mt,'Hours',po.hours,'Units/MT',po.units_per_mt]
            summary_format = workbook.add_format({'bold':True})
            summary_format.set_border()
            summary_format.set_align('center')
            row_counter = write_row(sheet,'A',summary_row_index,summary_row,summary_format)
        sheet.set_landscape()