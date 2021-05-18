import os
import sys
import pandas as pd

group_path = sys.argv[1]

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

print(f'Combining {x} Organization(s) Issues into {group_path}/combined.csv')
df.to_csv(f'{group_path}/combined.csv')
