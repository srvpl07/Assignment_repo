from flask import Flask
import requests
import json
from dateutil.parser import parse
import pytz 
from flask import request
import time
import re
from flask import jsonify

app = Flask(__name__)

@app.route("/1")
def first():

    shift_A = {
        "start": parse("6:00 AM IST").time(),
        "end": parse("2:00 PM IST").time()
    }
    shift_B = {
        "end": parse("8:00 PM IST").time(),
        "start": parse("2:00 PM IST").time()
    }
    res = {
        "shiftA" : {},
        "shiftB" : {},
        "shiftC" : {},

    }

    def compute_result(item, shift):
        for k in item.keys():
            if k!="time" and item[k]:
                if res[shift].get(k):
                    res[shift][k]+=1
                else:
                    res[shift][k] = 1

    tz_IST = pytz.timezone('Asia/Kolkata')
    response =  requests.get("https://gitlab.com/-/snippets/2094509/raw/master/sample_json_1.json")
    content_list = []
    if response.ok:
        content =  response.content
        content_list = json.loads(content)

    start_time = parse("{}".format(request.args.get('start_time')))
    end_time = parse("{}".format(request.args.get('end_time')))

    for item in content_list:
        dtime = parse(item.get("time"))
        if not dtime.utcoffset():
            dtime = parse(item.get("time")+"Z")

        if dtime>=start_time and dtime <= end_time:
            time = dtime.astimezone(tz_IST).time()
            if time>= shift_A.get("start") and time< shift_A.get("end"):

                compute_result(item, "shiftA")

            elif time>= shift_B.get("start") and time< shift_B.get("end"):
                compute_result(item, "shiftB")
            else:
                compute_result(item, "shiftC")

    #to_json= json.dumps(res)
    return jsonify(res)


@app.route("/2")
def second():

    res = {}
    def s_to_h(sec):
        ty_res = time.gmtime(sec)
        return time.strftime("%Hh:%Mm:%Ss",ty_res)
    response =  requests.get("https://gitlab.com/-/snippets/2094509/raw/master/sample_json_2.json")
    content_list = []
    if response.ok:
        content =  response.content
        content_list = json.loads(content)

    runtime = 0 
    downtime = 0
    start_time = parse("{}".format(request.args.get('start_time')))
    end_time = parse("{}".format(request.args.get('end_time')))

    for item in content_list:
        dtime = parse(item.get("time"))
        if not dtime.utcoffset():
            dtime = parse(item.get("time")+"Z")

        if dtime>=start_time and dtime <= end_time:
            r=item.get("runtime")
            d=item.get("downtime")
            if r>1021:
                runtime+=1021
                downtime+=d+r-1021
            else:
                runtime+=r
                downtime+=d
    utilisation = runtime*100/(runtime+downtime)


    res = {
    "runtime" : s_to_h(runtime),
    "downtime": s_to_h(downtime),
    "utilisation": "%0.2f" % utilisation

    }

    to_json= json.dumps(res)
    return to_json


@app.route("/3")
def third():

    res = {}

    response =  requests.get("https://gitlab.com/-/snippets/2094509/raw/master/sample_json_3.json")
    content_list = []
    if response.ok:
        content =  response.content
        content_list = json.loads(content)


    start_time = parse("{}".format(request.args.get('start_time')))
    end_time = parse("{}".format(request.args.get('end_time')))

    for item in content_list:
        dtime = parse(item.get("time"))
        if not dtime.utcoffset():
            dtime = parse(item.get("time")+"Z")

        if dtime>=start_time and dtime <= end_time:
            id = int(re.findall('[0-9]+',item.get("id"))[0])
            if item.get("state"):
                if id in res and "sum_belt2" in res[id] :
                    res[id]["sum_belt2"]+=item.get("belt2")
                    res[id]["count_belt2"]+=1
                else:
                    res[id] = {
                        "sum_belt2": item.get("belt2"),
                        "count_belt2": 1
                    }
            else:
                if id in res and "sum_belt1" in res[id]:
                    res[id]["sum_belt1"]+=item.get("belt1")
                    res[id]["count_belt1"]+=1
                else:
                    res[id] = {
                        "sum_belt1": item.get("belt1"),
                        "count_belt1": 1
                    }
    final_res = []
    for k in sorted(res.keys()):
        meta = {
            "id": k,
            "avg_belt1": res.get(k).get("sum_belt1", 0)//res.get(k).get("count_belt1",1),
            "avg_belt2": res.get(k).get("sum_belt2",0)//res.get(k).get("count_belt2",1)
        }
        final_res.append(meta)
    

    to_json= json.dumps(final_res)
    return to_json

#    return jsonify(results = final_res)  