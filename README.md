## Group CSV Export

This is a python script that utilizes the PySnyk module along with the Pandas modules to collect all issues from the report API and combine them into a single CSV for an entire group.

Pandas is used because the nature of issues and groups in Snyk being such that it could become a very large dataset, and Pandas has better large dataset handling than plain CSV libraries.

This is a poetry based project, if one already has poetry installed, running `poetry install; poetry shell` will be sufficient to deploy the needed dependencies for this to be run.

This script assumes one has set `SNYK_TOKEN` and `SNYK_GROUP` environment variables to use for retrieval of all the CSVs for a specific group. 

`python make_issue_csvs.py`

The script will find all issues that were reported as of "yesterday" (the calendar day before the script was run) and save them structured CSVs on the projects output directory. Since the dataset could be huge, we save the issues on a per project basis, allowing for this script to be run multiple times in case of error or timeouts causing one execution to fail. The script will resume where it left off and will only write a CSV of issues to disk once it has completed getting them all from the API. If it finds a CSV for a project already exists, it will skip that project on the next execution (if it is run on the same day).

`python join_csv.py output/2021-05-18/group-uid`

Once the script completes, running join_csv.py will collect all the CSVs on disk and save them to `output/2021-05-18/group-uid/combined.csv` 

