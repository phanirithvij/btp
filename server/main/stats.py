import calendar
import datetime
import os
from pathlib import Path

from flask import jsonify

from server.db import Database, UserFileSystem
from server.main import main

DB = Database("data/data.db")

STATS_OBJECT = {
    'type': 'line',
    'data': {
        'labels': [],
        'datasets': [{
            'data': [],
            'lineTension': 0,
            'backgroundColor': 'transparent',
            'borderColor': '#007bff',
            'borderWidth': 4,
            'pointBackgroundColor': '#007bff'
        }]
    },
    'options': {
        'scales': {
            'yAxes': [{
                'ticks': {
                    'beginAtZero': False
                }
            }]
        },
        'legend': {
            'display': False
        }
    }
}


@main.route('/userstats/<string:stype>')
def users_stats(stype: str):
    stats = {}
    if stype == "lastweek":
        daywise = [0 for x in range(7)]
        for u in DB.get_users():
            dateobj = (datetime.datetime.strptime(
                u['date(datetime_)'], "%Y-%m-%d"))
            oneweekago = datetime.datetime.now() - datetime.timedelta(days=7)
            # print(oneweekago)
            if dateobj > oneweekago:
                daywise[dateobj.isoweekday()-1] += 1
        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = daywise
        stats['data']['labels'] = list(calendar.day_name)
    elif stype == "lastmonth":
        curr = datetime.datetime.now()
        dayscount = calendar.monthrange(curr.year, curr.month)
        first_day_of_month = curr.replace(day=1)
        daysofmonth = [(first_day_of_month +
                        datetime.timedelta(i)).date().strftime('%d-%m-%Y') for i in range(dayscount[1])]
        # print(daysofmonth)
        daywise = [0 for x in range(dayscount[1])]
        for u in DB.get_users():
            dateobj = (datetime.datetime.strptime(
                u['date(datetime_)'], "%Y-%m-%d"))
            # https://stackoverflow.com/a/45266909/8608146
            if dateobj > curr.replace(day=1):
                daywise[dateobj.day-1] += 1

        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = daywise
        stats['data']['labels'] = daysofmonth
    elif stype == "lastyear":
        curr = datetime.datetime.now()
        firstday_of_year = curr.replace(day=1, month=1)
        months_of_year = [calendar.month_name[i+1] for i in range(12)]
        # print(daysofmonth)
        monthwise = [0 for x in range(12)]
        for u in DB.get_users():
            dateobj = (datetime.datetime.strptime(
                u['date(datetime_)'], "%Y-%m-%d"))
            if dateobj > firstday_of_year:
                monthwise[dateobj.month-1] += 1

        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = monthwise
        stats['data']['labels'] = months_of_year
    else:
        monthwise = {}
        for u in DB.get_users():
            dateobj = (datetime.datetime.strptime(
                u['date(datetime_)'], "%Y-%m-%d"))
            datestr = dateobj.date().strftime('%Y-%m-%d')
            if datestr not in monthwise:
                monthwise[datestr] = 0
            monthwise[datestr] += 1

        # https://stackoverflow.com/a/14472824/8608146
        keyssorted = sorted(list(monthwise.keys()))
        print(keyssorted)
        valuessorted = [monthwise[k] for k in keyssorted]
        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = valuessorted
        stats['data']['labels'] = keyssorted
    return jsonify(stats)


@main.route('/user/<string:username>/stats/<string:stype>')
def user_stats(username: str, stype: str):
    daywise = [0 for x in range(7)]
    for root, dirs, files in os.walk(UserFileSystem(username).user_dir()):
        for file in files:
            ctime = (os.stat(Path(root) / file).st_ctime)
            ctimed = (datetime.datetime.fromtimestamp(ctime))
            daywise[ctimed.isoweekday()-1] += 1

    stats = STATS_OBJECT.copy()
    stats['data']['datasets'][0]['data'] = daywise
    stats['data']['labels'] = list(calendar.day_name)
    return jsonify(stats)


@main.route('/stats/<string:stype>')
def dashb_stats(stype: str):
    stats = {}
    if stype == "lastweek":
        daywise = [0 for x in range(7)]
        for root, dirs, files in os.walk(UserFileSystem.users_dir()):
            for file in files:
                if file != "data.db":
                    ctime = (os.stat(Path(root) / file).st_ctime)
                    ctimed = (datetime.datetime.fromtimestamp(ctime))
                    # https://stackoverflow.com/a/45266909/8608146
                    oneweekago = datetime.datetime.now() - datetime.timedelta(days=7)
                    # print(file)
                    if ctimed > oneweekago:
                        daywise[ctimed.isoweekday()-1] += 1

        print(daywise)
        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = daywise
        stats['data']['labels'] = list(calendar.day_name)
    elif stype == "lastmonth":
        curr = datetime.datetime.now()
        dayscount = calendar.monthrange(curr.year, curr.month)
        first_day_of_month = curr.replace(day=1)
        daysofmonth = [(first_day_of_month +
                        datetime.timedelta(i)).date().strftime('%d-%m-%Y') for i in range(dayscount[1])]
        # print(daysofmonth)
        daywise = [0 for x in range(dayscount[1])]
        for root, dirs, files in os.walk(UserFileSystem.users_dir()):
            for file in files:
                if file != "data.db":
                    ctime = (os.stat(Path(root) / file).st_ctime)
                    ctimed = (datetime.datetime.fromtimestamp(ctime))
                    # https://stackoverflow.com/a/45266909/8608146
                    if ctimed > curr.replace(day=1):
                        daywise[ctimed.day-1] += 1

        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = daywise
        stats['data']['labels'] = daysofmonth
    elif stype == "lastyear":
        curr = datetime.datetime.now()
        firstday_of_year = curr.replace(day=1, month=1)
        months_of_year = [calendar.month_name[i+1] for i in range(12)]
        # print(daysofmonth)
        monthwise = [0 for x in range(12)]
        for root, dirs, files in os.walk(UserFileSystem.users_dir()):
            for file in files:
                if file != "data.db":
                    ctime = (os.stat(Path(root) / file).st_ctime)
                    ctimed = (datetime.datetime.fromtimestamp(ctime))
                    if ctimed > firstday_of_year:
                        monthwise[ctimed.month-1] += 1

        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = monthwise
        stats['data']['labels'] = months_of_year
    else:
        monthwise = {}
        for root, dirs, files in os.walk(UserFileSystem.users_dir()):
            for file in files:
                if file != "data.db":
                    ctime = (os.stat(Path(root) / file).st_ctime)
                    ctimed = (datetime.datetime.fromtimestamp(ctime))
                    datestr = ctimed.date().strftime('%Y-%m-%d')
                    if datestr not in monthwise:
                        monthwise[datestr] = 0
                    monthwise[datestr] += 1

        # mock
        # monthwise['2020-05-19'] = 21
        # monthwise['2012-12-21'] = 2
        # monthwise['2021-04-09'] = 233
        # monthwise['2019-05-12'] = 5
        # monthwise['2019-02-23'] = 441

        # https://stackoverflow.com/a/14472824/8608146
        keyssorted = sorted(list(monthwise.keys()))
        # print(keyssorted)
        valuessorted = [monthwise[k] for k in keyssorted]
        stats = STATS_OBJECT.copy()
        stats['data']['datasets'][0]['data'] = valuessorted
        stats['data']['labels'] = keyssorted

    return jsonify(stats)
