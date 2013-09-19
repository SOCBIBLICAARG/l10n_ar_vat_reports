import io
import os
import xmlrpclib
import base64

from lxml import etree

from datetime import date, datetime
import pytz

from osv import osv, fields

from tools import config
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _

from pentaho_reports.core import DEFAULT_OUTPUT_TYPE

# MOD: Parameters 
model = 'account.invoice'
report_name = 'sale_vat_report'  #defined in this module report/report_data.xml
#---------------------------------------------------------------------------------------------------------------

class sale_vat_report(osv.osv_memory):

    _name = "sale.vat.report"
    _description = "Sale Vat Report"

    _columns = {
                'output_type' : fields.selection([('pdf', 'Portable Document (pdf)'),('xls', 'Excel Spreadsheet (xls)'),('csv', 'Comma Separated Values (csv)'),\
                                                  ('rtf', 'Rich Text (rtf)'), ('html', 'HyperText (html)'), ('txt', 'Plain Text (txt)')],\
                                                  'Report format', help='Choose the format for the output', required=True),
# MOD: columns here
                'journal_ids': fields.many2many('account.journal', 'sale_vat_report_journal_rel', 'account_id', 'journal_id', 'Journals', domain=[('type','in',('sale','purchase','sale_refund','purchase_refund'))], required=True),
                'date_due': fields.date('Date Invoice'),
                'date_invoice': fields.date('Date Due'),\
                'amount_total': fields.float('Amount Total Greater Than',),
                # 'category_id': fields.many2one('res.partner.category', 'Category',),
                }

    
    def _get_output_type(self, cr, uid, context=None):
        
        if context is None:
            context = {}
        reports_obj = self.pool.get('ir.actions.report.xml')
        domain = [('report_name','=',report_name)]
        report_id = reports_obj.search(cr, uid, domain, limit=1)
        res = reports_obj.browse(cr, uid, report_id, context=context)[0].pentaho_report_output_type
        return res
    

    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[])

    
    _defaults = {
        'output_type': _get_output_type,
# MOD: adds defaults if neccesariy
        #'journal_ids': _get_all_journal,
    }

    def check_report(self, cr, uid, ids, context=None):

        wizard = self.browse(cr, uid, ids[0], context=context)
        
        if context is None:
            context = {}
        data = {}

        obj_model = self.pool.get(model)
        filters = []

# MOD: filters here        
        # Journals M2M
        # if wizard.journal_ids:
        filters.append(('journal_id','=', 1))                         
        # filters.append(('journal_id','in', [x.id for x in wizard.journal_ids]))                         
# No more modifications        
        
        model_ids = obj_model.search(cr, uid, filters, context=context)        
        data['ids'] = model_ids
        data['model'] = model
        data['output_type'] = wizard.output_type
#        data['variables'] = self._set_report_variables(wizard)

        return self._print_report(cr, uid, ids, data, context=context)


    def _print_report(self, cr, uid, ids, data, context=None):

        if context is None:
            context = {}

        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
    }



