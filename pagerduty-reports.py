import requests
from datetime import date, timedelta, datetime

API_ACCESS_KEY='e5SE6XJVdYuXJyhoxPui'
DAYS_BACK = 2

today_obj = date.today()
aweekago_obj = today_obj - timedelta(days=DAYS_BACK)
today_str = today_obj.strftime("%Y-%m-%d")
aweekago_str = aweekago_obj.strftime("%Y-%m-%d")


def pd_session(req):

    headers = {
        'Authorization': 'Token token={0}'.format(API_ACCESS_KEY),
        #'Content-type': 'application/json',
        'Accept': 'application/vnd.pagerduty+json;version=2'
    }
    payload = {
        'since':aweekago_str,
        'until':today_str,
        'status':'resolved',
        'limit': 10000,
    }
    r = requests.get(
                    'https://api.pagerduty.com/' + req,
                    headers=headers,
                    params=payload,
    )
    return r


def get_incidents_count():
    
    data = pd_session('incidents/count')
    return data.json()['total']
                    

def get_incidents_report():
    
    data = pd_session('incidents') 
    incidents = data.json()['incidents']   

    print("\nPagerDuty Incident Report from {0} to {1}\n".format(aweekago_str, today_str))
    print("Number of Incidents: {0}\n".format(get_incidents_count())) 

    headers = ['SERVICE', 'SUMMARY', 'CREATED_AT', 'ACKNOWLEDGED_AT', 'RESOLVED_AT', 'ACK_TIME (mins)', 'RESOL_TIME (mins)']
    print("{0:^14} {1:^54} {2:^24} {3:^24} {4:^24} {5:^16} {6:^16}".format(headers[0], headers[1], headers[2], headers[3], headers[4], headers[5], headers[6]))

    mttr_list = []
    mtta_list = []

    for incident in incidents:
        #print incident
        #inc_num = incident['incident_number']
        service_name = incident['service']['summary']
        inc_id = incident['id']
        summary = incident['summary'][:50]


        crt, ack, res = get_incident(inc_id)

        crt_obj = datetime.strptime(crt, '%Y-%m-%dT%H:%M:%SZ')
        res_obj = datetime.strptime(res, '%Y-%m-%dT%H:%M:%SZ')

        resolution_time_obj = res_obj - crt_obj
        resolution_time = resolution_time_obj.seconds / 60
        mttr_list.append(resolution_time)

        try:
            ack_obj = datetime.strptime(ack, '%Y-%m-%dT%H:%M:%SZ')
            ack_time_obj = ack_obj - crt_obj
            ack_time = ack_time_obj.seconds / 60
            mtta_list.append(ack_time)

        except:
            ack = ack_time = '-'
            

  
  
        print("{0:^14} {1:^54} {2:^24} {3:^24} {4:^24} {5:^16} {6:^16}".format(service_name, summary, crt, ack, res, ack_time, resolution_time))

    print("\nMTTR (Mean time to Resolve): %.2f\n" % (sum(mttr_list) / float(len(mttr_list))))
    print("MTTR (Mean time to Respond): %.2f\n" % (sum(mtta_list) / float(len(mtta_list))))


def get_incident(incident_id):

    data = pd_session('incidents/{0}/log_entries'.format(incident_id))
    log_entries = data.json()['log_entries']

    ack_obj_list = []     
    res_obj_list = []
    ack = ''
    res = '' 

    for entry in log_entries:
        if entry['type'] == 'acknowledge_log_entry':
            ack_time = entry['created_at']
            ack_obj = datetime.strptime(ack_time, '%Y-%m-%dT%H:%M:%SZ')
            ack_obj_list.append(ack_obj)

        if entry['type'] == 'resolve_log_entry':
            res_time = entry['created_at']
            res_obj = datetime.strptime(res_time, '%Y-%m-%dT%H:%M:%SZ')
            res_obj_list.append(res_obj)
        if entry['type'] == 'trigger_log_entry':
            crt = entry['created_at']
    try:
        ack = min(ack_obj_list).strftime("%Y-%m-%dT%H:%M:%SZ")
    except:
        ack = ''
    res = max(res_obj_list).strftime("%Y-%m-%dT%H:%M:%SZ")

    
    return crt,ack,res                    
        

def main():
    
    get_incidents_report()


if __name__ == "__main__":
    main()