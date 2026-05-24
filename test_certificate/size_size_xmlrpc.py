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
data_model2 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(data_url2))

corner_id = [26]
domain = [('corner_id', 'in', corner_id)]
data_list =  data_model.execute_kw(database, uid, password, 'size.size',
                                    'search_read', [domain])
# corner_id_dict = {21:4,22:5,20:3,24:7,23:6}  This dict id for Flats
# for i in data_list:
#     print(i.get("name").split("x"))
#     try:
#         width, thickness = i.get("name").split("x")
#         corner_id = i.get("corner_id")[0]
#         if corner_id:
#             record = {
#                 'shape':'flat',
#                 'corner_id':corner_id_dict.get(i.get('corner_id')[0]),
#                 'width_mm':float(width),
#                 'thickness_mm':float(thickness),
#             }
#             data_model2.execute_kw(database, uid2, password2, 'size.size',
#                                       'create', [record])
#     except Exception as e:
#         print("error:",e)
#         print("record:",record)
for i in data_list:
    try:
        dia =  i.get("name").split(" ")
        record = {
            'shape':'round',
            'diameter_mm':float(dia[1]),
        }
        data_model2.execute_kw(database, uid2, password2, 'size.size',
                                          'create', [record])
    except Exception as e:
        print(e)