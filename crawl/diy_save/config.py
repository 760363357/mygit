
# 模式选择
# MOTHED = 'mysql' or 'excel' or 'json'

# mysql配置
MYSQL = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'db': 'fil_u',
    'table': [{'table_name': 'url3'}, {'id': 'int auto_increment primary key'}, {'name': 'int'}, {'pro': 'varchar(20)'}]
}
# 单条数据模型，方便查看，没有用到
MYSQL_DATA = {
    'id': '',
    'name': '',
    'pro': ''
}


# Excel配置

EXCEL = {
    'path_dir': r'./',  # C:\Users\PYTHON\Desktop\service\tencent\tencent
    'filename': 'info.xls',
    'sheetname': 'My worksheet',
    'field': ['id', '企业名称', '编号', '社会信用代码/组织机构代码', '分类码', '省份', '法定代表人',
              '企业负责人', '质量负责人', '注册地址', '生产地址', '生产范围', '发证日期', '有效期至',
              '发证机关', '签发人', '日常监管机构', '日常监管人员', '监督举报电话', '备注', '相关数据库查询']
}

# 单条数据模型，方便查看，没有用到
EXCEL_DATA = {
    'id': '',
    'name': '',
    'pro': ''
}


# Json配置

JSON = {
    'path_dir': r'.',
    'filename': 'cookies.json'
}

# 单条数据模型，方便查看，没有用到
JSON_DATA = {
    'id': '',
    'name': '',
    'pro': ''
}