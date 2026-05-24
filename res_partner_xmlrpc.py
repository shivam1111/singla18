import xmlrpc.client
import ssl

data_url = "https://erp.singlasteel.in" # odoo instance url
context = ssl._create_unverified_context()
database = 'ssai' # database name
user = 'info@singlasteel.in' # username
password = 'd1995fb6b8af84731b4ea2172041d7ca01d8e907' # api key
common_auth = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(data_url),context=context)
uid = common_auth.authenticate(database, user, password, {})

data_url2 = "http://www.singlasteel.in" # odoo instance url
password2  = "shivam"
user2 = 'info@singlasteel.in' # username
common_auth2 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(data_url2),context=context)
uid2 = common_auth2.authenticate(database, user2, password2, {})


data_model = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(data_url),context=context)
domain = [('id', 'not in', [1,3])]
old_ids =  data_model.execute_kw(database, uid, password, 'res.partner',
                                    'search', [domain])
res_partner_fields =  ['name', 'email','ref','phone','mobile',
                        'website','street','street2','zip','city']
data_list = data_model.execute_kw(database, uid, password,
                                  'res.partner', 'read', [old_ids, res_partner_fields])
print(data_list)

data_model2 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(data_url2))
data_model2.execute_kw(database, uid2, password2,
                      'res.partner', 'write', [[], {'country_id': 104}])
# # 3. Write to New Server
# for record in data_list:
#     # Remove the 'id' field if it was returned, Odoo 18 will generate a new one
#     if 'id' in record: del record['id']
#     try:
#         new_id = data_model2.execute_kw(database, uid2, password2,
#                                        'res.partner', 'create', [record])
#         print(f"Migrated: {record['name']} -> New ID: {new_id}")
#     except Exception as e:
#         print(f"Failed to migrate {record.get('name')}: {e}")



# result = data_model2.execute_kw(database, uid2, password2, 'res.partner',
#                                     'create',partner_id)
# element_id =  data_model.execute_kw(database, uid, password, 'chemical.element', 'search', [[]])

# element_df = pd.DataFrame(element_data)
# print("Old Element Table\n",element_df)
#
# element_idn =  data_model2.execute_kw(database, uid2, password2, 'chemical.element', 'search', [[]])
# element_datan = data_model2.execute_kw(database, uid2, password2, 'chemical.element', 'read', [element_idn],{'fields':['name','code']})
# element_dfn = pd.DataFrame(element_datan)
# print("New Element Table \n",element_dfn)
# #
# grade_id =  data_model.execute_kw(database, uid, password, 'material.grade', 'search', [[]])
# grade_data = data_model.execute_kw(database, uid, password, 'material.grade', 'read', [grade_id],{'fields':['name']})
# grade_df = pd.DataFrame(grade_data)
# # print("Old Element Table\n",grade_df)
# #
# grade_idn =  data_model2.execute_kw(database, uid2, password2, 'material.grade', 'search', [[]])
# grade_datan = data_model2.execute_kw(database, uid2, password2, 'material.grade', 'read', [grade_idn],{'fields':['name']})
# grade_dfn = pd.DataFrame(grade_datan)
# # print("New Element Table\n",grade_dfn)
#
# heat_id = data_model.execute_kw(database, uid, password, 'heat.heat', 'search', [[['create_date','>=','07-01-2024']]])
# heat_id=[17199]
# heat_data = data_model.execute_kw(database, uid, password, 'heat.heat', 'read', [heat_id])
#
# for heat in heat_data:
#     vals={
#         'date':heat.get('date'),
#         'xrf_tested':heat.get('xrf_tested'),
#         'partner_id':False,
#         'grinding':heat.get('grinding',False),
#         'surface_inspection':heat.get('surface_inspection',False),
#         'state':heat.get('state'),
#         'truck_no':heat.get('truck_no'),
#         'furnace_heat_no':heat.get('furnace_heat_no'),
#     }
#     gr_id = heat.get('grade_id',False)
#     gr_idn = False
#     line_ids_data = []
#     if gr_id:
#         gr_name = grade_df.query('id==%s' % gr_id[0]).get('name').to_list()
#         if gr_name:
#             gr_idn = grade_dfn.query("name=='%s'" % gr_name[0]).get('id').to_list()
#     vals.update({'grade_id':gr_idn and gr_idn[0] or False})
#     composition_lines_data = data_model.execute_kw(database, uid, password, 'composition.line', 'read', [heat.get('line_ids')])
#     for i in composition_lines_data:
#         el_id = i.get('element_id', False)
#         print("el_id",el_id)
#         el_idn = False
#         if el_id:
#             el_code = element_df.query('id==%s' % el_id[0]).get('code').to_list()
#             print('el_code',el_code)
#             if el_code:
#                 el_idn = element_dfn.query("code=='%s'" % el_code[0]).get('id').to_list()
#                 print('el_idn',el_idn)
#             line_ids_data.append([
#             0,0,{
#                 'element_id':el_idn and el_idn[0] or False,
#                 'min_val':i.get('min_val'),
#                 'max_val':i.get('max_val'),
#                 'furnace_val':i.get('furnace_val'),
#                 'actual_val':i.get('actual_val'),
#             }
#         ])
#     vals.update({'line_ids':line_ids_data})
#     print(vals)
#     data_model2.execute_kw(database, uid2, password2, 'heat.heat', 'create', [vals])
