import os
import json
import requests

from yandex_tracker_client import TrackerClient
headers = {"Accept": "application/json", "Authorization":"OAuth " + os.environ['TOKEN'], "X-Org-Id":os.environ['ORG']}
org_header = os.environ['ORG']
token = os.environ['TOKEN']


def handler(event, context):
    teamUsers = []
    users_dict = {} 
    print ("------------------------- start new autoassignment --------------------------")  
    try:
        client = TrackerClient(token=token, org_id=org_header)
        headers = {"Accept": "application/json", "Authorization":"OAuth " + token, "X-Org-Id":org_header}
        issue = client.issues[event['queryStringParameters']['id']] 
    except:
        print ("API exception")
# поиск списка пользователей команды очереди
    try:
        url = 'https://api.tracker.yandex.net/v2/queues/' + issue.queue.key + '?expand=team'
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        teamUsers = data['teamUsers']
    except:
        print ("can't get queue team from api")                    
    for user in teamUsers:
        issues = client.issues.find(filter={'assignee': user['id'], 'resolution': 'empty()', 'queue': issue.queue.key}) 
        users_dict[user] = len(issues)
# выбор исполнителя с минимальным количеством задач
    assign_to = min(users_dict, key=users_dict.get)
# назначение исполнителя 
    try:
        print (str(assign_to) +" auto-assigned, has " + str(users_dict[assign_to]) + " open tasks")
        issue.update(assignee=assign_to)	
        comment = issue.comments.create(text="auto-assigned , " + str(users_dict[assign_to]) + " open tasks")						
    except Exception as e:
        print (e)
    return {
        'statusCode': 200,
        'body': str(assign_to) +' auto-assigned, has ' + str(users_dict[assign_to]) + ' open tasks',
    }
