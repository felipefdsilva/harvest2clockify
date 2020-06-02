from time import sleep
import pandas as pd
import numpy as np
import requests
import random
import json

"""
*  Rate Limit: 10 requests per second
"""

BASE_ENDPOINT = 'https://api.clockify.me/api/v1'
WORKSPACE_ID = '5ebc89d346cf2748cd5c5b90'
CLIENT_PATH = '/workspaces/{}/clients'
PROJECT_PATH = '/workspaces/{}/projects'
TASK_PATH = '/workspaces/{}/projects/{}/tasks'
PERSONAL_KEY = ''

headers = {
    "X-Api-Key": PERSONAL_KEY,
    "Content-Type": "application/json"
}

def get_clients(filename):
    df = pd.read_csv(filename)

    df['Payload'] = df.apply(lambda x: json.dumps({"name": x['Client Name']}), axis=1)
    return df['Payload'].values

def get_ids(url_path, columns):
    url = BASE_ENDPOINT + url_path.format(WORKSPACE_ID)
    response = requests.request(
        "GET",
        url,
        headers=headers,
    )
    try:
        response.raise_for_status()
    except:
        print(json.dumps(response.json(), indent=4, default=str))

    ids = [item['id'] for item in response.json()]
    names = [item['name'] for item in response.json()]

    return pd.DataFrame(np.array([ids, names]).T.tolist(), columns=columns)

def generate_color_hex_code():
    r = lambda: random.randint(0,255)
    color = '#{:02x}{:02x}{:02x}'.format(r(),r(),r())
    return color

def generate_list_of_colors(df):
    colors = []
    for entry in df['Client'].values:
        colors.append(generate_color_hex_code())
        sleep(0.3)

    return colors

def get_projects(filename):
    df = pd.read_csv(filename)
    df = df[['Client', 'Project']]
    df['color'] = generate_list_of_colors(df)

    clients_df = get_ids(CLIENT_PATH, ['clientId', 'Client'])
    df = df.merge(clients_df, on='Client', how='right')

    df['Payload'] = df.apply(
        lambda x: json.dumps(
            {
                "name": x['Project'], 
                "clientId": x['clientId'], 
                "color":x['color']
            }
        ), 
        axis=1
    )
    return df['Payload'].values

def get_tasks(filename, project_id):
    df = pd.read_csv(filename)
    
    payloads = []
    for task in df['Task name'].values:
        payload = {
            "projectId": project_id,
            "name": task
        }
        payloads.append(json.dumps(payload.copy()))
    
    return payloads

def post(url, payloads):
    request_count = 0

    for payload in payloads:
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=payload
        )
        try:
            response.raise_for_status()
        except:
            print(json.dumps(response.json(), indent=4, default=str))
        
        request_count+=1
        if request_count == 10:
            request_count = 0
            sleep(1)

    return "Data Imported"

def main():
    print("Importing Clients")
    payloads = get_clients('harvest_data/clients.csv')
    url = BASE_ENDPOINT + CLIENT_PATH.format(WORKSPACE_ID)
    post(url, payloads)

    print("Importing Projects")
    payloads = get_projects('harvest_data/projects.csv')
    url = BASE_ENDPOINT + PROJECT_PATH.format(WORKSPACE_ID)
    post(url, payloads)

    print("Importing Tasks")
    projects_df = get_ids(PROJECT_PATH, ['projectId', 'Project'])
    for project_id in projects_df['projectId'].values:
        payloads = get_tasks('harvest_data/tasks.csv', project_id)
        url = BASE_ENDPOINT + TASK_PATH.format(WORKSPACE_ID, project_id)
        post(url, payloads)

    print("Done")

if __name__ == "__main__":
    main()
