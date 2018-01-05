#!/usr/bin/env python3


import MySQLdb as mdb


HOST = 'localhost'
USER = 'orm'
PASSWD = 'orm'
DB = 'orm'
PORT = 3306
CHARSET = 'utf8'

conn = mdb.connect(
        host=HOST, user=USER, password=PASSWD,
        database=DB, port=PORT, charset=CHARSET
        )
cursor = conn.cursor()

def dec(cls):
    cls.tb_name = cls.__name__.lower()
    attrs = cls.__dict__
    fields = [k for k, v in attrs.items() if isinstance(v, Field)]
    fields.sort()
    cls.fields = fields

    return cls


class Field:

    def validate(self, model, attr_name):
        value = getattr(model, attr_name, None)
        if value is None:
            raise AttributeError('field "%s" is not set' % attr_name)
        return value


class CharField(Field):

    def __init__(self, max_length):
        if not isinstance(max_length, int):
            raise AttributeError('invalid parameter "max_length"')
        self.max_length = max_length

    def validate(self, model, name):
        value = Field.validate(self, model, name)
        if not isinstance(value, str) or len(value) > self.max_length:
            raise AttributeError('invalid value of field "%s"' % name)


class IntegerField(Field):

    def __init__(self, default):
        if not isinstance(default, int):
            raise AttributeError('invalid parameter "default"')
        self.default = default

    def validate(self, model, name):
        value = Field.validate(self, model, name)
        if value is None:
            value = self.default
        if not isinstance(value, int):
            raise AttributeError('invalid value of field "%s"' % name)


class Model:
    pk = None

    def __init__(self, **kargs):
        for k, v in kargs.items():
            if k not in self.fields:
                raise AttributeError('"%s" is not a defined field' % k)
            setattr(self, k, v)

    def validate(self):
        for attr_name in self.fields:
            getattr(self.__class__, attr_name).validate(self, attr_name)

    def save(self):
        self.validate()
        if getattr(self, 'pk', None) == None:
            self.insert()
        else:
            self.update()

    def insert(self):
        sql = 'insert into %s(%s) values(%s)'
        fields = ','.join(self.fields)
        values = [getattr(self, k) for k in self.fields]
        sql = sql % (
                self.tb_name,
                fields,
                ','.join('%s' for k in self.fields)
                )
        if cursor.execute(sql, values):
            self.pk = cursor.lastrowid
            conn.commit()

    def update(self):
        sql = 'update %s set %s where id=%s'
        sql = sql % (
                self.tb_name,
                ','.join('%s=%%s' % k for k in self.fields ),
                self.pk
                )
        values = [getattr(self, k) for k in self.fields]
        if cursor.execute(sql, args=values):
            conn.commit()

    def delete(self):
        sql = 'delete from %s where id=%s' % (self.tb_name, self.pk)
        if cursor.execute(sql):
            conn.commit()

    @classmethod
    def query(cls, **kargs):
        keys = list(kargs)
        if not keys:
            sql = 'select * from %s' % cls.tb_name
            r = cursor.execute(sql)
        else:
            values = tuple(kargs[k] for k in keys)
            sql = 'select * from %s where %s'
            sql = sql % (
                    cls.tb_name,
                    ' and '.join('%s=%%s' % k for k in keys)
                    )
            r = cursor.execute(sql, args=values)

        if r:
            results = []
            for item in cursor.fetchall():
                result = cls(**dict(zip(cls.fields, item[1:])))
                result.pk = item[0]
                yield result

@dec
class Stu(Model):
    name = CharField(max_length=16)
    age = IntegerField(default=0)


if __name__ == "__main__":
    stu = Stu(name='lee', age=18)
    stu.save()
    stus = Stu.query()
    stu = next(stus)
    print(stu.name, stu.age)
    stu.name = 'tom'
    print(stu.name, stu.age)
    stu.save()

