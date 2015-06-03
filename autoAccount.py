#!/usr/bin/env python
# -*- coding: utf-8 -*-
import db
import yaml
import torndb
import time
import utils
from datetime import datetime
from models import week_user,users,orders
from utils import YamlLoader
TIME_SLEEP = 12*60*60
#TIME_SLEEP = 200
MYSQL_DATE_FM = "%Y-%m-%d %H:%M:%S"
SETTINT_FLIE = "settings.yaml"
try :
    config = yaml.load (file(SETTINT_FLIE,'r'),YamlLoader)
    log_path = config['weekaction']['weekaction_log']
except yaml.YAMLError as e:
    print "Error in configuration file :%s " % e
    quit()

def main():
    db.mysql = torndb.Connection(**config['mysql'])
    while True:
        flag = check_valid_date()
        if flag == -1:
            pass

        elif flag == 1:
            users_info = week_user.get_left_user()
            dump2csv(log_path,users_info)
            for user in users_info:
                dealwith_user(user)
            return

        else:
            users_info = week_user.get_7day_users()
            dump2csv(log_path,users_info)
            for user in users_info:
                dealwith_user(user)
            #lock_with_uid
        time.sleep(TIME_SLEEP)

def dump2csv(file_path,recodes):
    import csv
    with open(file_path+str(datetime.now())+'weekaction.csv','wb+') as csvfile:
        spamwriter = csv.writer(csvfile)
        head = ['ID','用户ID','参与时间','任务分']
        keys = ['id','uid','time','week_points']
        spamwriter.writerow(head)
        for row in recodes:
            ls = []
            for key in keys:
                ls.append(row[key])
            spamwriter.writerow(ls)

def dealwith_user(user):
    prize = get_prize_grade_next_stage(user['week_points'])
    prize = prize[0]
    user_user = users.get_info_by_uid(user['uid'])
    if user_user:
        users.add_total_points(user_user,prize)
        now_points = user_user['points'] + prize
   #log msg
        info = "%s 基本积分%s ,获得额外奖励 %s,当前剩余积分%s"\
            %(user['uid'],user['week_points'],prize,now_points)
        week_user.reset_week_user(user['uid'])
        orders.new_global_order(
            user['uid'],prize,user_user['points'],
            orders.ORDER_TYP_PRORATA_WEEK,
            "周活动奖励：基本积分%s 获得奖励%s" %(user['week_points'],prize)
	    )
    else:
        info = "%s 不存在" % user['uid']

    utils.print_log("autoAccount",log_path,info)

def get_prize_grade_next_stage(points):
    prorata_table=week_user.get_week_prize_prorata()
    prize = 0
    grade = None
    next_stage = None
    for pr in prorata_table:
        if points > pr['points']:
            prize = int(pr['prorata']*points)/100
            grade = pr['grade']
            break;
        else :
            next_stage =pr['points']
    return prize,grade,next_stage

def check_valid_date():
    global config
    stop_date = config['weekaction']['stop']
    begin_date = config['weekaction']['begin']
    ts = time.strptime(stop_date,MYSQL_DATE_FM)
    tb = time.strptime(begin_date,MYSQL_DATE_FM)
    if datetime.now()<datetime(tb.tm_year,tb.tm_mon,tb.tm_mday,tb.tm_hour,tb.tm_min,tb.tm_sec):
        return -1
    elif datetime.now()>datetime(ts.tm_year,ts.tm_mon,ts.tm_mday, ts.tm_hour,ts.tm_min,ts.tm_sec):
        return 1
    return 0


#no in use
#def check_user_in_date(uid):
#    user = week_user.get_info(uid)
#    if (datetime.now()-timedelta(days=7)) > user['time']:
#	return False
#    return True

if __name__ == "__main__" :
    main()
