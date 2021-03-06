#!/usr/bin/python

import csv
import getopt
import os
import sys
import tempfile
from tempfile import NamedTemporaryFile

import gspread
from jira import JIRA


def get_issues(jql, **kwargs):
    start_at = ""
    max_results = ""
    if kwargs:
        if kwargs["start_at"]:
            start_at = kwargs["start_at"]
        if kwargs["max_results"]:
            max_results = kwargs["max_results"]
    return (
        jira.search_issues(jql, startAt=start_at, maxResults=max_results)
        if kwargs
        else jira.search_issues(jql)
    )


def update_google_sheet(file, **kwargs):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    gc = gspread.service_account(filename="./client_secret.json", scopes=scope)
    sheet = gc.open("MySheet")
    content = open(file, "r").read()
    gc.import_csv(sheet.id, content)


def generate_sheet_data(jql, **kwargs):
    # with NamedTemporaryFile(suffix='.csv', mode='w+') as csvfile:
    with open("text.csv", "w+") as csvfile:
        worksheet = csv.writer(csvfile, delimiter=",")
        worksheet.writerow(
            [
                "key",
                "title",
                "created",
                "updated",
                "automation_status",
                "label",
                "reporter",
            ]
        )
        issues = get_issues(
            jql, start_at=kwargs["start_at"], max_results=10000
        )
        for issue in issues:
            key = issue.key
            title = issue.raw["fields"]["summary"]
            created = issue.raw["fields"]["created"].split("T")[0]
            updated = issue.raw["fields"]["updated"].split("T")[0]
            automation_status = issue.raw["fields"]["customfield_14517"][
                "value"
            ]
            reporter = issue.raw["fields"]["reporter"]["name"]
            try:
                label = (
                    None
                    if issue.raw["fields"]["labels"] == []
                    else issue.raw["fields"]["labels"]
                )
            except:
                label = None
            worksheet.writerow(
                [
                    key,
                    title,
                    created,
                    updated,
                    automation_status,
                    label,
                    reporter,
                ]
            )
            csvfile.read()
        # update_google_sheet(csvfile.name)


def main(argv):
    jira_username = ""
    jira_password = ""
    extra_args = {}
    try:
        opts, args = getopt.getopt(argv, "u:p:f:s:d:")
        if opts == [] or "-u" not in dict(opts) or "-p" not in dict(opts):
            print(
                f"your jira username (-u) and password (-p) must be passed as"
                f" arguments\nUsage:\ngenerate_jira_report.py"
                f" -u <jira_username> -p <jira_password> -f <jira_filter>"
            )
            sys.exit(2)
    except getopt.GetoptError:
        print(
            "generate_jira_report.py -u <jira_username> -p <jira_password> -f <jira_filter>"
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-u":
            jira_username = arg
        elif opt == "-p":
            jira_password = arg
        elif opt == "-f":
            extra_args["filter"] = arg
        elif opt == "-s":
            extra_args["start_at"] = arg
        elif opt == "-d":
            extra_args["from_date"] = arg

    return jira_username, jira_password, extra_args


if __name__ == "__main__":
    jira_username, jira_password, extras = main(sys.argv[1:])
    server = "https://jira.takealot.com/jira/"
    username = os.environ.get("JIRA_USERNAME", jira_username)
    password = os.environ.get("JIRA_PASSWORD", jira_password)

    jira = JIRA(options={"server": server}, basic_auth=(username, password))
    from_date = extras.get("from_date")

    jql = (
        extras.get("filter")
        if extras.get("filter")
        else f'project = "Quality Assurance - Engineering" and'
        f' issuetype = "Test Case Template" and reporter in'
        f' ("meimoen.adams@takealot.com", "leroy.hanslo@takealot.com",'
        f' "rifaat.royepen@takealot.com", "Nkhabiseng.Mabaleka@takealot.com",'
        f' "pinkie.dyantyi@takealot.com") and Automation != null and'
        f' created >= "{from_date}"  ORDER BY  created desc'
    )
    start_at = extras.get("start_at") if extras != {} else 0
    generate_sheet_data(jql, start_at=start_at, max_value=10000)
