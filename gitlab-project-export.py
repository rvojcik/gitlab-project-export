#!/usr/bin/env python3

from __future__ import print_function
import sys
import os
import argparse
import yaml
from datetime import date
import requests
import re
import time
# Find our libs
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from gitlab_export import config, gitlab


return_code = 0

if __name__ == '__main__':
    # Parsing arguments
    parser = argparse.ArgumentParser(
        description="""
        GitLab Project Export is
        small project using Gitlab API for exporting whole gitlab
        project with wikis, issues etc.
        Good for migration or simple backup your gitlab projects.
        """,
        epilog='Created by Robert Vojcik <robert@vojcik.net>')

    # Arguments
    parser.add_argument(
        '-c', dest='config', default='config.yaml',
        help='config file'
    )
    parser.add_argument(
        '-d', dest='debug', default=False, action='store_const',
        const=True, help='Debug mode'
    )

    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print("Unable to find config file %s" % (args.config))

    c = config.Config(args.config)
    token = c.config["gitlab"]["access"]["token"]
    gitlab_url = c.config["gitlab"]["access"]["gitlab_url"]
    ssl_verify = c.config["gitlab"]["access"]["ssl_verify"]

    # Check if there is wait between exports in config
    if 'wait_between_exports' in c.config["gitlab"]:
        wait_between_exports = c.config["gitlab"]["wait_between_exports"]
    else:
        wait_between_exports = 0

    # Check if there is membership in config
    if 'membership' in c.config["gitlab"]:
        membership = c.config["gitlab"]["membership"]
    else:
        membership = True

    # Init gitlab api object
    if args.debug:
        print("%s, token" % (gitlab_url))
    gitlab = gitlab.Api(gitlab_url, token, ssl_verify)

    # Export each project
    export_projects = []

    # Get All member projects from gitlab
    projects = gitlab.project_list(membership=str(membership))
    if not projects:
        print("Unable to get projects for your account", file=sys.stderr)
        sys.exit(1)

    # Check projects against config
    # Create export_projects array
    for project_pattern in c.config["gitlab"]["projects"]:
        for gitlabProject in projects:
            if re.match(project_pattern, gitlabProject):
                export_projects.append(gitlabProject)

    if args.debug:
        print("Projects to export: " + str(export_projects))

    for project in export_projects:
        if args.debug:
            print("Exporting %s" % (project))

        # Download project to our destination
        if c.config["backup"]["project_dirs"]:
            destination = c.config["backup"]["destination"] + "/" + project
        else:
            destination = c.config["backup"]["destination"]

        # Create directories
        if not os.path.isdir(destination):
            try:
                os.makedirs(destination)
            except:
                print("Unable to create directories %s" % (destination), file=sys.stderr)
                sys.exit(1)

        if args.debug:
            print(" Destination %s" % (destination))

        # Prepare actual date
        d = date.today()
        # File template from config
        file_tmpl = c.config["backup"]["backup_name"]
        # Projectname in dest_file
        dest_file = destination + "/" + file_tmpl.replace(
            "{PROJECT_NAME}",
            project.replace("/", "-")
        )
        # Date in dest_file
        dest_file = dest_file.replace(
            "{TIME}", d.strftime(c.config["backup"]["backup_time_format"]))

        if args.debug:
            print(" Destination file %s" % (dest_file))

        if os.path.isfile(dest_file):
            print("File %s already exists" % (dest_file), file=sys.stderr)
            return_code += 1
            continue

        status = gitlab.project_export(project)

        # Export successful
        if status:
            if args.debug:
                print("Success for %s" % (project))
            # Get URL from gitlab object
            url = gitlab.download_url["api_url"]
            if args.debug:
                print(" URL: %s" % (url))

            # Download file
            r = requests.get(
                url,
                allow_redirects=True,
                stream=True,
                verify=ssl_verify,
                headers={"PRIVATE-TOKEN": token})

            if r.status_code >= 200 and r.status_code < 300:
                with open(dest_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            else:
                print(
                    "Unable to download project %s. Got code %d: %s" % (
                        project,
                        r.status_code,
                        r.text),
                    file=sys.stderr)
                return_code += 1

        else:
            # Export for project unsuccessful
            print("Export failed for project %s" % (project), file=sys.stderr)
            return_code += 1
        
        # If set, wait between exports
        if args.debug:
            print("Waiting between exports for %d seconds" % (wait_between_exports))
        time.sleep(wait_between_exports)

    sys.exit(return_code)
