#!/usr/bin/env python3
# coding=utf-8

import pymysql
import sqlite3
from pymysql.connections import Connection
from pymysql.cursors import SSDictCursor
from pymysql.connections import Connection as MyConnection


class MysqlConn():
    def db_connector(self) -> Connection:
        """
        功能:用于数据库初始化连接，获取db实例对象
        :return: db连接对象
        """
        common_db_config = {'host': '10.211.55.18',
                            'user': 'root',
                            'port': 3306,
                            'passwd': '',
        		    		'db': 'wordpress',
                            'charset': 'utf8mb4',
                            'cursorclass': pymysql.cursors.DictCursor,
                            'autocommit': False}
        try:
            conn: Connection = pymysql.connect(**common_db_config)
            return conn
        # 防止mysql连接失败时一顿虾条，多写点提示，考虑到以后可能要在服务器命令行环境下运行会有乱码先酱紫~
        except pymysql.MySQLError as e:
            print(str(e))

class DBConnector(object):
    def __init__(self):
        self.db: MyConnection = MysqlConn().db_connector()
        self.cur: SSDictCursor = self.db.cursor()

db=DBConnector()
"""
# query category
sql= "select term_id,name from wp_terms where term_id>=4 and term_id<=10"

# query tag
sql = "select wp_term_taxonomy.term_id,wp_terms.name from wp_term_taxonomy,wp_terms where wp_term_taxonomy.taxonomy = 'post_tag' and wp_term_taxonomy.term_id=wp_terms.term_id"

# query post
sql="select ID,post_date,post_content,post_title,post_name,comment_status from wp_posts where post_status='publish' and post_type='post';"

# find duplicated post
data_list = [d['object_id'] for d in data]
import collections
print([item for item, count in collections.Counter(data_list).items() if count > 1])]

# query category relation
sql= "SELECT  t.term_id, tr.object_id FROM wp_terms AS t  INNER JOIN wp_term_taxonomy AS tt ON t.term_id = tt.term_id INNER JOIN wp_term_relationships AS tr ON tr.term_taxonomy_id = tt.term_taxonomy_id INNER JOIN wp_posts ON tr.object_id=wp_posts.ID WHERE tt.taxonomy='category'"

# query tag relation
sql= "SELECT  t.term_id, tr.object_id FROM wp_terms AS t  INNER JOIN wp_term_taxonomy AS tt ON t.term_id = tt.term_id INNER JOIN wp_term_relationships AS tr ON tr.term_taxonomy_id = tt.term_taxonomy_id INNER JOIN wp_posts ON tr.object_id=wp_posts.ID WHERE tt.taxonomy='post_tag'"

# query comments
sql="select comment_ID,comment_post_ID,comment_author,comment_author_email,comment_date,comment_content,comment_parent from wp_comments;"
"""

db.cur.execute(sql)
data = db.cur.fetchall()


"""
# insert category
sqlite3_sql = "INSERT INTO BLOG_CATEGORY (ID,CATEGORY_NAME) VALUES ({id},'{name}')".format(
id=d['term_id'],name=d['name'])

# insert tag
sqlite3_sql = "INSERT INTO BLOG_TAG (ID,TAG_NAME) VALUES ({id},'{name}')".format(id=d['term_id'],name=d['name'])

# insert post
sqlite3_sql = "INSERT INTO BLOG_POST (ID,TITLE,SLUG,POST_DATE,CONTENT,AUTHOR_ID,COMMENT_STATUS) VALUES (?,?,?,?,?,?,?)"
sqlite3_cur.execute(sqlite3_sql,(d['ID'],d['post_title'],d['post_name'],d['post_date'],d['post_content'],1,'open'))

# insert category relation
sqlite3_query_posts_sql = "select id from blog_post"
sqlite3_cur.execute(sqlite3_query_posts_sql)
sqlite3_query_posts_results =[data[0] for data in sqlite3_cur.fetchall()]
for q_p_result in sqlite3_query_posts_results:
    for cate_relation in data:
        if q_p_result == cate_relation['object_id']:
            sql = "update blog_post set category_id={cate_id} where id={post_id}".format(cate_id=cate_relation['term_id'],
            post_id=q_p_result)
            print(sql)
            sqlite3_cur.execute(sql)    

# insert tag relation
for d in data:
    sql = "insert into blog_post_tag (post_id, tag_id) values ({post_id},{tag_id})".format(post_id=d['object_id'],
    tag_id=d['term_id'])
    print(sql)
    sqlite3_cur.execute(sql)  

# insert comment
for d in data:
    sql = "insert into blog_comments (id,post_id,user_name,email,comment_date,content,comment_parent,approved) values ('{id}','{post_id}','{user_name}','{email}','{date}','{content}','{parent}','{approved}')".format(
        id=d['comment_ID'],post_id=d['comment_post_ID'],user_name=d['comment_author'],email=d['comment_author_email'],
        date=d['comment_date'],content=d['comment_content'],parent=d['comment_parent'],approved='approved'
    )
    print(sql)
    sqlite3_cur.execute(sql)
"""


sqlite3_conn=sqlite3.connect('db.sqlite3')
sqlite3_cur= sqlite3_conn.cursor()



sqlite3_conn.commit()
print("Records created successfully")
sqlite3_conn.close()
