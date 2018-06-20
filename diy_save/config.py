
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
    'path_dir': r'./save',  # C:\Users\PYTHON\Desktop\service\tencent\tencent
    'filename': 'topics1.xls',
    'sheetname': 'topic',
    'field': ['id', 'topics', 'topics_id', 'topic', 'link']
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