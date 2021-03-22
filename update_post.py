#!/usr/bin/env python
# encoding=utf-8
"""
@author: v_linlgan
@contact: v_linlgan@tencent.com
@software: Pycharm 2020.2
@file: update_post.py
@time: 2021/1/1-14:15
@desc:
"""
import sqlite3
sqlite3_conn=sqlite3.connect('db.sqlite3')
sqlite3_cur= sqlite3_conn.cursor()
select_sql = 'select id, content from blog_post'
sqlite3_cur.execute(select_sql)
select_results = sqlite3_cur.fetchall()
# print(select_results)
for data in select_results:
    # content_new = data[1].replace('http://10.211.55.18', 'https://www.sharpgan.com')
    # if 'python%e7%88%ac%e8%99%ab' in data[1]:
    content_new = data[1].replace('python%e8%84%9a%e6%9c%ac', 'category/Python%e8%84%9a%e6%9c%ac')
    update_sql = "update blog_post set content=? where id={0}".format(data[0])
    print(update_sql)
    sqlite3_cur.execute(update_sql, (content_new,))

sqlite3_conn.commit()
print("Records created successfully")
sqlite3_conn.close()
