import pymysql
from .config import MYSQL, EXCEL, JSON
import xlwt
import xlrd
import os
import json


class Saver(object):
    '''
    excel，json的增删改操作都要使用save方法才能保持，sql的直接操作文件了
    '''
    def __init__(self, mode='excel', info=None):
        self.__mode = mode
        if mode == 'mysql':
            if info:
                for key in info:
                    MYSQL[key] = info[key]
            self.__db = Sql(MYSQL['host'], MYSQL['port'], MYSQL['user'], MYSQL['password'], MYSQL['db'], MYSQL['table'])
        elif mode == 'excel':
            if info:
                for key in info:
                    EXCEL[key] = info[key]
            self.__db = Excel(EXCEL['filename'], EXCEL['sheetname'], EXCEL['path_dir'], EXCEL['field'])
            # e = Excel(FILENAME, SHEETNAME, PATH_DIR, FIELD)
        else:
            if info:
                for key in info:
                    JSON[key] = info[key]
            self.__db = Json(JSON['filename'], JSON['path_dir'])

    def insert(self, data_dict, index=None):
        if self.__mode == 'mysql':
            self.__db.insert(data_dict)
        else:
            self.__db.insert(data_dict, index)

    def remove(self, condition_dict):
        self.__db.remove(condition_dict)

    def update(self, data_dict, conditon_dict=None):
        self.__db.update(data_dict, conditon_dict)

    def get(self, conditon_dict=None, count=None):
        return self.__db.get(conditon_dict, count)

    def mv_repeat(self, key_field, reverser=False):
        if self.__mode == 'excel' or self.__mode == 'json':
            self.__db.mv_repeat(key_field, reverser)

    def clear(self):
        self.__db.clear()

    def save(self):
        if self.__mode == 'excel' or self.__mode == 'json':
            self.__db.save()

    def __call__(self, *args, **kwargs):
        print('这是一个{}数据库对象'.format(self.__mode.upper()))


class Sql(object):
    '''连接数据库，使用数据表并提供增删改（无返回值）查（返回值是查到的数据）功能'''
    def __init__(self, host, port, user, password, db, table):
        self.__con = pymysql.connect(host=host, port=port, user=user, password=password, charset='utf8')
        self.__db = db
        self.__table_name = table.pop(0)['table_name']
        self.__fields = table
        self.__cur = self.__con.cursor()
        self.init_table()

    def init_table(self):
        '''
        初始化数据库，根据配置查看是否存在该数据库和表，如果存在，则直接使用，否则创建，并使游标
        进入到数据库中，随时操作配置信息中的表。
        :return:
        '''
        self.__cur.execute('''
                                show databases
                ''')
        res = self.__cur.fetchall()
        if self.__db not in [x[0] for x in res]:
            print('因为配置中的数据库不存在，故创建数据库')
            sql = 'create database ' + self.__db
            self.__cur.execute(sql)
            self.__con.commit()
        sql = 'use ' + self.__db
        self.__cur.execute(sql)
        try:
            sql = 'create table ' + self.__table_name + '('
            for di in self.__fields:
                for key in di:
                    sql = sql + key + ' ' + di[key] + ','
            sql = sql[:-1] + ')'
            self.__cur.execute(sql)
            self.__con.commit()
        except pymysql.err.InternalError as e:
            pass

    def insert(self, data_dict):
        '''
        插入数据，传入的参数可以是单条数据对应数据表字段的字典，也可以是多条数据的列表。
        :param data_dict: 这样的格式：{'id': '2'}, {'name': '12', 'pro': '212'}， 必要参数
        :return:
        '''
        if isinstance(data_dict, dict):
            sql = 'insert into ' + self.__table_name + ' set '
            datas = data_dict.items()
            for item in datas:
                sql += item[0] + '=' + item[1] + ','
            sql = sql[:-1]
        elif isinstance(data_dict, list):
            sql = 'insert into ' + self.__table_name + '('
            keys = list(data_dict[0].keys())
            for key in keys:
                sql += key + ','
            sql = sql[:-1] + ')' + ' ' + 'values'
            for data in data_dict:
                sql += '('
                for key in keys:
                    sql += data[key] + ','
                sql = sql[:-1] + '),'
            sql = sql[:-1]
        else:
            print('插入数据时输入不知名类型数据，拒绝操作！')
            raise TypeError
        try:
            self.__cur.execute(sql)
            self.__con.commit()
            print('插入数据成功！')
        except pymysql.err.IntegrityError as e:
            print('插入数据失败!', e)

    def remove(self, data_dict=None):
        '''
        删除数据，根据条件data_dict字典删除对应的数据。
        :param data_dict: 该参数可以为空，也可以为条件字典；为空时，表示删除整个表数据，为
                           条件字典时，如：{'name': '10'}，删除所有列中name=10的行，即删除部分数据。 非必要参数

        :return:
        '''
        com = []
        if not data_dict:
            sql = 'delete from ' + self.__table_name
            com.append(sql)
        if isinstance(data_dict, dict):
            sql = 'delete from ' + self.__table_name + ' ' + 'where '
            for data in data_dict:
                sql += data + '=' + data_dict[data] + ','
            sql = sql[:-1]
            com.append(sql)
        elif isinstance(data_dict, list):
            for data in data_dict:
                sql = 'delete from ' + self.__table_name + ' ' + 'where '
                for key in data:
                    sql += key + '=' + data[key] + ','
                sql = sql[:-1]
                com.append(sql)
        # else:
        #     print('删除数据时输入不知名类型数据，拒绝操作！')
        #     raise TypeError
        try:
            print(com)
            res = [self.__cur.execute(i) for i in com]
            self.__con.commit()
            print('删除数据成功！')
        except pymysql.err.IntegrityError as e:
            print('删除数据失败！', e)

    def update(self, data_dict, condition_list=None):
        '''
        更新行信息.
        :param condition_list: 条件，可以为空，字典，列表， 为空时表示根据data_dict来更新所有列，为条件字典时表示根据条件更新，
                                为列表时，表示根据每一个条件字典来多次更新数据。非必要参数。
        :param data_dict:更新的字段，只能是字典格式，表示列的更新， 必要参数
        :return:
        '''
        assert isinstance(data_dict, dict)
        com = []
        sql = 'update ' + self.__table_name + ' ' + 'set '
        for data in data_dict:
            sql += data + '=' + data_dict[data] + ','
        sql = sql[:-1]
        if not condition_list:
            com.append(sql)
        if isinstance(condition_list, dict) and condition_list:
            sql_f = ' where '
            for key in condition_list:
                sql_f += key + '=' + condition_list[key] + ','
            sql_f = sql_f[:-1]
            sql += sql_f
            com.append(sql)
        elif isinstance(condition_list, list) and condition_list:
            for condi in condition_list:
                sql_f = ' where '
                for key in condi:
                    sql_f += key + '=' + condi[key] + ','
                sql_f = sql_f[:-1]
                com.append(sql + sql_f)
        try:
            res = [self.__cur.execute(sql) for sql in com]
            self.__con.commit()
            print('更新数据成功！')
        except pymysql.err.IntegrityError as e:
            print('更新数据失败！', e)

    def get(self, conditon_dict=None, count=None):
        '''
        获取查询的数据
        :param conditon_dict: 条件字典，可以为空和字典，为空时表示无条件查询，否则根据条件查询，非必要参数
        :param count:  表示查询的数量，可以为空也可以为整数；为空时返回条件字典的全部数据，为整数时返回特定数量的数据。
        :return:
        '''
        sql = 'select * from ' + self.__table_name
        if conditon_dict:
            sql += ' where '
            for condi in conditon_dict:
                sql += condi + '=' + conditon_dict[condi] + ','
            sql = sql[:-1]
        try:
            self.__cur.execute(sql)
        except pymysql.err.IntegrityError as e:
            print('获取数据失败！', e)
        else:
            res = self.__cur.fetchmany(count) if count else self.__cur.fetchall()
            print(f'成功获取到{len(res)}条数据！')
            return res

    def clear(self):
        self.remove()

    def __del__(self):
        self.__cur.close()
        self.__con.close()


class Excel(object):
    '''
    通过初始化将xls文件读入内存中，并对其修改保存。
    '''
    def __init__(self, filename, sheetname, path_dir, field):
        self.__path_dir = path_dir
        self.__file = filename
        self.__sheet = sheetname
        self.__field = field
        self.__table = self.initdata()
        # print(self.__table)

    def initdata(self):
        '''
        初始化文件，如果工作目录存在目标文件，则读取其文件内容，否则创建文件并设置字段
        :return:
        '''
        res = os.listdir(self.__path_dir)
        # print(self.__path_dir)
        # print(res)
        # print(self.__path_dir + '/' +self.__file)
        if self.__file in res:
            data = xlrd.open_workbook(self.__path_dir + '/' +self.__file)
            sheet = data.sheet_by_name(self.__sheet)
            result = [sheet.row_values(num) for num in range(sheet.nrows)]
            if self.__field not in result:
                result = [self.__field] + result
        else:
            data = xlwt.Workbook(encoding='utf-8')
            sheet = data.add_sheet(self.__sheet)
            for num in range(len(self.__field)):
                sheet.write(0, num, label=self.__field[num])
            data.save(self.__path_dir + '/' + self.__file)
            result = [self.__field]
        return result

    def insert(self, data_dict, index=None):
        '''
        数据的插入，可以按行插入
        :param data_dict: 只能是列表或者字典，插入一条数据或者多条数据，必要参数
        :param index: 整数，数据插入的位置，默认在末尾插入数据，也可以设置索引插入
        :return:
        '''
        if isinstance(data_dict, list):
            if isinstance(data_dict[0], dict):
                if index:
                    self.__table.insert(index, [data_dict[key] for key in self.__field])
                else:
                    self.__table.append([data_dict[key] for key in self.__field])
            else:
                if index:
                    self.__table.insert(index, data_dict)
                else:
                    self.__table.append(data_dict)

        elif isinstance(data_dict, dict):
            if index:
                self.__table.insert(index, [data_dict.get(key) for key in self.__field])
            else:
                self.__table.append([data_dict.get(key) for key in self.__field])
        else:
            print('不支持添加数据的类型！')
            raise TypeError
        print('插入数据成功！')

    def remove(self, condiction_list):
        '''
        数据的删除操作，可以删一条或多条数据,删除的数据不包含字段头。
        :param condiction_list: 字典或者列表，表示根据条件删除数据
        :return:
        '''
        if isinstance(condiction_list, list):
            if isinstance(condiction_list[0], dict):
                for data_dict in condiction_list:
                    li = [data_dict.get(key, 'erro') for key in self.__field]
                    res = li.count('erro')
                    for i in self.__table[1:]:
                        o = 0
                        for num in range(len(i)):
                            if li[num] == i[num]:
                                o += 1
                        if len(li) - res == o:
                            self.__table.remove(i)
            else:
                for num in range(self.__table[1:].count(condiction_list)):
                    self.__table.remove(condiction_list)
        elif isinstance(condiction_list, dict):
            li = [condiction_list.get(key, 'erro') for key in self.__field]
            res = li.count('erro')
            for i in self.__table[1:]:
                o = 0
                for num in range(len(i)):
                    if li[num] == i[num]:
                        o += 1
                if len(li) - res == o:
                    self.__table.remove(i)
        else:
            print('输入类型错误！')
            raise TypeError
        print('删除数据成功！')
        # print(self.__table)

    def update(self, data_dict, condition_list=None):
        '''
        更新数据操作，可以更新一条或多条数据字段
        :param data_dict: 字典，更新后的数据字段
        :param condition_list: 可以为空，字典或者列表，为空时表示更新所有数据的字段；为字典时，只更新特定条件的数据；
                                列表是字典的一种条件扩展，表示多次更新
        :return:
        '''
        data = [data_dict.get(key, 'erro') for key in self.__field]
        if not condition_list:
            for i in range(1, len(self.__table)):
                for n in range(len(data)):
                    if data[n] == 'erro':
                        continue
                    self.__table[i][n] = data[n]
        elif isinstance(condition_list, dict):
            con_data = [condition_list.get(key, 'erro') for key in self.__field]
            res = con_data.count('erro')
            for i in range(1, len(self.__table)):
                count = 0
                for n in range(len(con_data)):
                    if con_data[n] == 'erro':
                        continue
                    if self.__table[i][n] == con_data[n]:
                        count += 1
                if len(con_data) - res == count:
                    for n in range(len(data)):
                        if data[n] == 'erro':
                            continue
                        self.__table[i][n] = data[n]
        elif isinstance(condition_list, list):
            assert isinstance(condition_list[0], dict)
            for cond_dict in condition_list:
                con_data = [cond_dict.get(key, 'erro') for key in self.__field]
                res = con_data.count('erro')
                for i in range(1, len(self.__table)):
                    count = 0
                    for n in range(len(con_data)):
                        if con_data[n] == 'erro':
                            continue
                        if self.__table[i][n] == con_data[n]:
                            count += 1
                    if len(con_data) - res == count:
                        for n in range(len(data)):
                            if data[n] == 'erro':
                                continue
                            self.__table[i][n] = data[n]
        else:
            print('输入类型有误！')
            raise TypeError
        print('更新数据成功！')

    def get(self, condition_dict=None, count=None):
        '''
        获取数据，根据条件获取或者根据数量获取
        :param condition_dict: 可以为空，字典，列表；为空时表示无条件查找，配合count使用。为条件字典时，表示根据条件查找特定
                                信息，列表是字典的一种拓展
        :param count:可以为空，也可以是整数；为空时表示查找的所有数据都返回；为整数时表示返回的最大信息数为该整数。
        :return:
        '''
        def a(data_dict):
            result = []
            data = [data_dict.get(key, 'erro') for key in self.__field]
            res = data.count('erro')
            for i in self.__table[1:]:
                o = 0
                for num in range(len(i)):
                    if data[num] == i[num]:
                        o += 1
                if len(data) - res == o:
                    result.append(i)
            return result
        if not condition_dict and count:
            res = []
            for value in self.__table[1:]:
                di = {}
                for num in range(len(self.__field)):
                    di[self.__field[num]] = value[num]
                res.append(di)
            return res[:count]
        elif not condition_dict and not count:
            res = []
            for value in self.__table[1:]:
                di = {}
                for num in range(len(self.__field)):
                    di[self.__field[num]] = value[num]
                res.append(di)
            return res
        elif isinstance(condition_dict, dict):
            rsl = a(condition_dict)
            res = []
            for value in rsl:
                di = {}
                for num in range(len(self.__field)):
                    di[self.__field[num]] = value[num]
                res.append(di)
            if count:
                res = res[:count]
            return res
        elif isinstance(condition_dict, list):
            assert isinstance(condition_dict[0], dict)
            res = []
            for con_data in condition_dict:
                rsl = a(con_data)
                for value in rsl:
                    di = {}
                    for num in range(len(self.__field)):
                        di[self.__field[num]] = value[num]
                    res.append(di)
            # res = list(set(res))
            if count:
                res = res[:count]
            res = [tuple(item.items()) for item in res]
            res = list(set(res))
            res = [dict(item) for item in res]
            return res

    def clear(self):
        self.__table = []

    def save(self):
        data = xlwt.Workbook(encoding='utf-8')
        sheet = data.add_sheet(self.__sheet)
        # print(self.__table)
        for row in range(len(self.__table)):
            for col in range(len(self.__table[row])):
                sheet.write(row, col, label=self.__table[row][col])
        try:
            data.save(self.__path_dir + '/' + self.__file)
            print(self.__path_dir + '/' + self.__file)
        except PermissionError as e:
            print('保存的Excel文件已被其他进程打开！', e)
            raise PermissionError
        print('保存文件成功！')

    def mv_repeat(self, key_field, reverser=False):
        assert isinstance(key_field, str)
        num = self.__field.index(key_field)
        print(num)
        tu = map(lambda x: tuple(x), self.__table[1:])
        res = map(lambda x: list(x), sorted(set(tu), key=lambda x: x[num], reverse=reverser))
        self.__table = [self.__field] + list(res)
        print('成功去重！')


class Json(object):
    '''
    JSON文件的增删改查
    '''
    def __init__(self, filename, path_dir):
        self.__file = filename
        self.__path_dir = path_dir
        self.__data = self.initdata()
        # print(self.__data)

    def initdata(self):
        '''
        初始化数据，将文件中的内容读入
        :return:
        '''
        res = os.listdir(self.__path_dir)
        if self.__file in res:
            with open(self.__path_dir + '/' + self.__file, 'r') as fi:
                try:
                    reslut = json.load(fi)
                except json.decoder.JSONDecodeError as e:
                    reslut = []
                    pass
        else:
            with open(self.__path_dir + '/' + self.__file, 'w') as fi:
                json.dump([], fi)
            reslut = []
        return reslut

    def insert(self, data_dict, index=None):
        '''
        插入数据
        :param data_dict: 可以是字典或者列表，为字典时表示插入一条数据，为列表表示插入多条数据
        :param index: 可以为空，也可以是数字；为空时表示追加插入，为数字时表示从某个位置插入
        :return:
        '''
        if isinstance(index, int):
            if isinstance(data_dict, dict):
                self.__data.insert(index, data_dict)
            elif isinstance(data_dict, list):
                assert isinstance(data_dict[0], dict)
                for di in range(len(data_dict)):
                    self.__data.insert(index+di, data_dict[di])
            else:
                print('不支持的数据类型！')
                raise TypeError
        else:
            if isinstance(data_dict, dict):
                self.__data.append(data_dict)
            elif isinstance(data_dict, list):
                assert isinstance(data_dict[0], dict)
                for di in data_dict:
                    self.__data.append(di)
            else:
                print('不支持的数据类型！')
                raise TypeError
        print('插入数据成功！')

    def remove(self, condition_data):
        '''
        根据条件删除数据
        :param condition_data: 可以为字典或者列表，为字典时表示根据条件删除，列表是字典的一种拓展，表示多次根据条件删除。
        :return:
        '''
        if isinstance(condition_data, dict):
            res = self.__remove(condition_data)
            li = [self.__data.remove(x) for x in res]
        elif isinstance(condition_data, list):
            for condi_dict in condition_data:
                res = self.__remove(condi_dict)
                li = [self.__data.remove(x) for x in res]
        else:
            print('输入的数据类型无法识别！')
            raise TypeError
        print('删除数据成功！')

    def __remove(self, data_dict):
        '''
        传入条件字典，得到符合数据的列表
        :param data_dict:
        :return:
        '''
        condi_keys = data_dict.keys()
        num = len(condi_keys)
        li = []
        for data in self.__data:
            data_keys = data.keys()
            count = 0
            for i in condi_keys:
                if i in data_keys:
                    count += 1
            if num == count:
                count = 0
                for i in condi_keys:
                    if data_dict[i] == data[i]:
                        count += 1
                if num == count:
                    li.append(data)
        # res = [self.__data.remove(x) for x in li]
        return li

    def update(self, data_dict, condi_dict=None):
        '''
        根据条件来更新数据。
        :param data_dict: 字典，表示更新的字段
        :param condi_dict: 空，字典，或者列表。为空时表示更新每一条数据中符合字段的数据；为字典时，表示根据条件更新，先找到
                          对应的数据，然后再更新该数据中存在符合需要更新字段的数据。为列表时表示多次查找并更新，是字典的一种扩展。
        :return:
        '''
        assert isinstance(data_dict, dict)
        if not condi_dict:
            for data in range(len(self.__data)):
                keys = self.__data[data].keys()
                for key in keys:
                    if key in data_dict.keys():
                        self.__data[data][key] = data_dict[key]
        elif isinstance(condi_dict, dict):
            self._update(data_dict, condi_dict)
        elif isinstance(condi_dict, list):
            assert isinstance(condi_dict[0], dict)
            for condi in condi_dict:
                self._update(data_dict, condi)
        else:
            print('存在不支持的类型！')
            raise TypeError
        print('更新数据成功！')

    def _update(self, data_dict, condi):
        '''
        传入更新的字典和条件字典，然后进行对应的更新
        '''
        condi_keys = condi.keys()
        num = len(condi_keys)
        for data in range(len(self.__data)):
            data_keys = self.__data[data].keys()
            count = 0
            for i in condi_keys:
                if i in data_keys:
                    count += 1
            if num == count:
                count = 0
                for i in condi_keys:
                    if condi[i] == self.__data[data][i]:
                        count += 1
                if num == count:
                    for key in data_dict:
                        if key in data_keys:
                            self.__data[data][key] = data_dict[key]

    def get(self, condi_dict=None, count=None):
        '''
        获取数据，返回含有字典的列表
        :param condi_dict: 为空，字典；为空时表示无条件查找。为字典时表示根据条件查找数据。
        :param count: 为空或者数字；为空时表示返回查找的所有数据；为数字时表示返回count条数据。
        :return:
        '''
        if not count and not condi_dict:
            return self.__data
        elif not condi_dict and count > 0:
            return self.__data[:count]
        elif condi_dict:
            assert isinstance(condi_dict, dict)
            res = self.__remove(condi_dict)
            print('获取数据成功!')
            if count and count < len(res):
                return res[:count]
            else:
                return res

    def clear(self):
        self.__data = []

    def mv_repeat(self, key_field, reverser=False):
        assert isinstance(key_field, str)
        # print(self.__data)
        # print(self.__data[0].items())
        tu = map(lambda x: tuple(x.items()), self.__data)
        res = set(tu)
        res = [dict(x) for x in res]
        res.sort(key=lambda x: x.get(key_field, len(self.__data)), reverse=reverser)
        # res = sorted(res, key=lambda x: dict(x).get(key_field, len(self.__data)), reverse=reverser)
        print(res)
        # self.__data = list(res)
        print('成功去重！')

    def save(self):
        '''
        将之前的所有操作保存到文件中。
        :return:
        '''
        with open(self.__path_dir + '/' + self.__file, 'w') as fi:
            json.dump(self.__data, fi)


# if __name__ == '__main__':
#     s = Saver('json')
#     s.clear()
#     s.save()
    # j = Json(JFILENAME, PATH_DIR)
    # j.mv_repeat('name', reverser=True)
    # j.insert([{'id': 3.0, 'name': 50}, {'id': 2.0, 'name': 52}])
    # j.remove([{'id': 3.0}])
    # res = j.get({'id': 3.0})
    # print(res)
    # j.update({'name': 99},  [{'id': 3.0}])

    # e = Excel(FILENAME, SHEETNAME, PATH_DIR, FIELD)
    # e.insert({'id': 'heihie', 'name': 3.8})
    #
    # e.mv_repeat('name', reverser=True)
    # res = e.save()
    #
    # print()
    # e.remove([{'name': 2.0, 'id': '链表'}])
    # e.insert({'id':1, 'name':2, 'pro':3})
    # l = [[1, 2], 2, 3, 1]
    # i = [1]
    #
    # print(i in l)
    # s = Sql(MYSQL['host'], MYSQL['port'], MYSQL['user'], MYSQL['password'], MYSQL['db'], MYSQL['table'])
    # s.insert({'name': '4', 'id': '4', 'pro': '101'})
    # s.remove([])
    # s.update({'id': '2'}, {'name': '12', 'pro': '212'})
    # s.update([{'name': '10'}, {'id': '2'}], {'name': '10', 'pro': '212'})
    # s.get({})
