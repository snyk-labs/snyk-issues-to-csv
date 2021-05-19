import snyk
import datetime
import os
import pandas as pd

def process_org(org, client, date_path, the_date):
    org_id = org.id

    org_path = os.path.join(date_path,f'org-{org_id}')
    
    if os.path.isdir(org_path) is not True:
        os.mkdir(org_path)

    # This currently just gets all projects in an org, but the snyk library supports filtering by tags
    # https://github.com/snyk-labs/pysnyk#projects 
    projects = client.organizations.get(org_id).projects.all()

    for p in projects:
        update_project_issues(p.id, client, org_id, org_path, the_date)

def update_project_issues(p_id, client, org_id, o_path, the_date):
    
    project_csv = os.path.join(o_path,f'{p_id}.csv')

    if os.path.isfile(project_csv):
        print(f'{datetime.datetime.now()}: Issues already cached for {p_id} from {org_id}')
    else:
        print(f'{datetime.datetime.now()}: Getting issues for {p_id} from {org_id}')
        save_project_issues(p_id, client, org_id, project_csv, the_date)

def save_project_issues(p_id, client, org_id, project_csv, the_date):

    i_filter = {'filters':{'orgs':[org_id],'projects':[p_id]}}
    
    # this lets us get a total issue count so we can do pagination
    # this is using the low level client of the snyk library
    # https://github.com/snyk-labs/pysnyk#low-level-client
    # combined with our reporting api endpoint:
    # https://snyk.docs.apiary.io/#reference/reporting-api/issues/get-list-of-issues

    ireq = client.post(f'reporting/issues/?from={the_date}&to={the_date}&page=1&perPage=1&sortBy=issueTitle&order=asc&groupBy=issue', i_filter)

    total = ireq.json()['total']

    per_page = 250
    page_count = (total // per_page) + 1

    df = pd.DataFrame()

    for x in range(1,page_count+1):
        req = client.post(f'reporting/issues/?from={the_date}&to={the_date}&page={x}&perPage={per_page}&sortBy=issueTitle&order=asc&groupBy=issue', i_filter)
        results = req.json()['results']
        for y in results:
            y['project.repo'] = y['projects'][0]['name'].split(':')[0]
            y.update({f'project.{k}':v for k,v in y['projects'][0].items()})
            y.pop('projects',None)
            y.update({f'issue.{k}':v for k,v in y['issue'].items()})
            y.pop('issue',None)
            y['issue.isFixed'] = y['isFixed']
            y.pop('isFixed',None)
            y['issue.introducedDate'] = y['introducedDate']
            y.pop('introducedDate',None)
        
        df = df.append(pd.DataFrame.from_dict(results))
        
    #project_issues.extend(results)

    df.reset_index(drop=True, inplace=True)

    if df.empty:
        print(f'{datetime.datetime.now()}: No issues for {p_id} from {org_id}')
    else:
        print(f'{datetime.datetime.now()}: Saving issues from {p_id} to {project_csv}')
        print(df)
        df.to_csv(project_csv,index=False)


snyktoken = os.environ['SNYK_TOKEN']

snykgroup = os.environ['SNYK_GROUP']

# this sets the session to include retries in case of api timeouts etc
client = snyk.SnykClient(snyktoken, tries=3, delay=1, backoff=1)

yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)

the_date = yesterday.strftime('%Y-%m-%d')

print(f'{datetime.datetime.now()}: Gathering all issues for all orgs with group ID: {snykgroup} for ({the_date})')

# Gets current working directory
cwd_path = os.getcwd()

output_dir = os.path.join(cwd_path, 'output')

if os.path.isdir(output_dir) is not True:
    os.mkdir(output_dir)

date_path = os.path.join(output_dir, the_date)

if os.path.isdir(date_path) is not True:
    os.mkdir(date_path)

group_path = os.path.join(date_path, f'group-{snykgroup}')

if os.path.isdir(group_path) is not True:
    os.mkdir(group_path)

# remove the phantom orgs that are really the groups
orgs = [ y for y in client.organizations.all() if hasattr(y.group,'id') ]
# remove orgs that don't match the snykgroup
orgs = [ y for y in orgs if y.group.id == snykgroup ]

for org in orgs:
    process_org(org, client, group_path, the_date)

print(f'{datetime.datetime.now()}: Completed gathering issues into folder: {group_path}')
print(f'{datetime.datetime.now()}: To combine into one CSV run `python join_csv.py {group_path}`')