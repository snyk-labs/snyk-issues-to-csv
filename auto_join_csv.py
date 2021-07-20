import os
import sys
import pandas as pd
import datetime

yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
the_date = yesterday.strftime('%Y-%m-%d')

cwd_path = os.getcwd()

output_dir = os.environ.get('SNYK_OUTPUT_DIR', os.path.join(cwd_path, 'output'))

snykgroup = os.environ['SNYK_GROUP']

group_path = os.path.join(output_dir, f'{the_date}/group-{snykgroup}')

if os.path.isdir(group_path) is not True:
    raise ValueError(f'No folder at the path {group_path}')

csvs = []
for root, dirs, files in os.walk(group_path, topdown=False):
   for name in files:
      if name.endswith('csv') and name != 'combined.csv':
          csvs.append(os.path.join(root,name))

df = pd.DataFrame()
x = 1
for csv in csvs:
    df = df.append(pd.read_csv(csv,header=0,encoding='UTF-8'))
    df.reset_index(drop=True, inplace=True)
    x += 1

print(f'Combining {x} Project(s) Issues into {group_path}/combined.csv')
df.to_csv(f'{group_path}/combined.csv')
