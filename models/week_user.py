#!/usr/bin/env python
# -*- coding : utf-8 -*-
import db
from datetime import datetime,timedelta

DEADLINE = 7
def check_in(uid):
    r = db.mysql.query(
        "SELECT uid FROM weekaction WHERE uid=%s " ,uid)
    if not r:
        return False
    return True
def update_time(uid):
        return db.mysql.execute(
        "UPDATE weekaction SET time=%s WHERE uid=%s" ,datetime.now() ,uid)

def new_user(uid):
    return db.mysql.execute(
        "INSERT INTO weekaction (uid) VALUES(%s) ",uid)

def get_info(uid):
    return db.mysql.get(
        "SELECT * FROM weekaction WHERE uid=%s " , uid)

def inc_invite(user_info):
    week_invite = int (user_info['week_invite']) +1
    db.mysql.execute(
        "UPDATE weekaction SET week_invite=%s WHERE uid=%s" , week_invite,user_info['uid'])

def inc_points(user_info,points):
    week_points = int(user_info['week_points']) + points
    db.mysql.execute(
        "UPDATE weekaction SET week_points=%s WHERE uid=%s " ,week_points,user_info['uid'])

def get_7day_users():
    return db.mysql.query(
        "SELECT * FROM weekaction WHERE  time < %s " ,(datetime.now()-timedelta(days=DEADLINE)))
        #"SELECT * FROM weekaction WHERE  time < %s " ,(datetime.now()-timedelta(seconds=DEADLINE)))

def reset_week_user(uid):
   # return db.mysql.execute(
   #     "UPDATE weekaction SET week_invite=0 , week_points=0, time=%s WHERE uid=%s" ,datetime.now(),uid)
   return db.mysql.execute(
         "DELETE FROM weekaction where uid=%s",uid)

def get_week_prize_prorata():
    return db.mysql.query(
        "SELECT * FROM weekprorata ORDER BY points DESC")

def get_left_user():
    return db.mysql.query(
	"SELECT * FROM weekaction"
	)
def test():
   #print "creating new user with uid  %s" %sys.argv[1]
    #new_user(sys.argv[1])
    #print "updateting the time using %s" %datetime.now()
    #time.sleep(1)
    #update_time(sys.argv[1])
    #print "geting the user(%s) info " %sys.argv[1]
    #user = get_info(sys.argv[1])
    #inc_invite(user[0])
    #inc_points(user[0],1000)
    #reset_week_user(0)
    print check_in(10002)
    user_7=get_7day_users()
    for user in user_7 :
        print user['uid'],user['time'],user['week_points']

    #print "Showing the prize prorata table"
    #prorata = get_week_prize_prorata()
    #for i in prorata:
    #    print i

