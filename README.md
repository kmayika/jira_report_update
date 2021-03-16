This package is used to update spreadsheet with data from Jira.

# Pre-equisite
To run this script you will first need to create a service account and auth credentials by running these steps:

1. Go to the Google APIs Console.
2. Create a new project.
3. Click Enable API. Search for and enable the Google Drive API.
4. Create credentials for a Web Server to access Application Data.
5. Name the service account and grant it a Project Role of Editor.
6. Download the JSON file.
7. Copy the JSON file to your code directory and rename it to client_secret.json

# Running the script

```
$ python generate_jira_report.py -u <jira_username> -p <jira_password> -f <jira_filter>
```
