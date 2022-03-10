#!/usr/bin/env python3

from __future__ import print_function
import os
import re
import sys
import time
import argparse
from datetime import datetime
import requests
from gitlab_export import config, gitlab

# Find our libs
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


return_code = 0

if __name__ == '__main__':
    # Parsing arguments
    parser = argparse.ArgumentParser(
        description="""
        GitLab Project Export is a
        small project using GitLab API for exporting whole gitlab
        project with wikis, issues etc.
        Good for migration or simple backup of your gitlab projects.
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
    parser.add_argument(
        '-f', dest='force', default=False, action='store_const',
        const=True, help='Force mode - overwrite backup file if exists'
    )
    parser.add_argument(
        '-n', dest='noop', default=False, action='store_const',
        const=True, help='Only print what would be done, without doing it'
    )

    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print("Unable to find config file %s" % (args.config))

    c = config.Config(args.config)
    token = c.config["gitlab"]["access"]["token"]
    gitlab_url = c.config["gitlab"]["access"]["gitlab_url"]
    ssl_verify = c.config["gitlab"]["access"]["ssl_verify"]

    # Check additional config
    wait_between_exports = c.config['gitlab'].get('wait_between_exports', 0)
    membership = c.config['gitlab'].get('membership', True)
    include_archived = c.config['gitlab'].get('include_archived', False)
    max_tries_number = c.config['gitlab'].get('max_tries_number', 12)
    retention_period = c.config['backup'].get('retention_period', 0)
    exclude_projects = c.config["gitlab"].get('exclude_projects', [])
    if not ((type(retention_period) == int or type(retention_period) == float) and (retention_period >= 0)):
        print("Invalid value for retention_period. ignoring")
        retention_period = 0

    # Init gitlab api object
    if args.debug:
        print("%s, token" % (gitlab_url))
    gitlab = gitlab.Api(gitlab_url, token, ssl_verify)

    # Export each project
    export_projects = []

    # Get All member projects from gitlab
    projects = gitlab.project_list(membership=str(membership), archived=str(include_archived))
    if not projects:
        print("Unable to get projects for your account", file=sys.stderr)
        sys.exit(1)

    # Check projects against config
    # Create export_projects array
    for project_pattern in c.config["gitlab"]["projects"]:
        for gitlabProject in projects:
            if re.match(project_pattern, gitlabProject):
                export_projects.append(gitlabProject)

    # Remove any projects that are marked as excluded
    for ignored_project_pattern in exclude_projects:
        for gitlabProject in projects:
            if re.match(ignored_project_pattern, gitlabProject):
                if args.debug:
                    print("Removing project '%s' from export (exclusion: '%s'): " % (str(gitlabProject), str(ignored_project_pattern)))
                export_projects.remove(gitlabProject)

    if args.debug:
        print("Projects to export: " + str(export_projects))

    if args.noop:
        print("Not running actual export because of -n/--noop flag.")
        sys.exit(0)

    for project in export_projects:
        if args.debug:
            print("Exporting %s" % (project))

        # Download project to our destination
        destination = c.config["backup"]["destination"]
        if c.config["backup"]["project_dirs"]:
            destination += "/" + project

        # Create directories
        if not os.path.isdir(destination):
            try:
                os.makedirs(destination)
            except Exception:
                print("Unable to create directories %s" % (destination), file=sys.stderr)
                sys.exit(1)

        if args.debug:
            print(" Destination %s" % (destination))

        # Prepare actual date
        d = datetime.now()
        # File template from config
        file_tmpl = c.config["backup"]["backup_name"]
        # Projectname in dest_file
        dest_file = destination + "/" + file_tmpl.replace(
            "{PROJECT_NAME}",
            project.replace("/", "-")
        )
        # Date in dest_file
        dest_file = dest_file.replace(
            "{TIME}", d.strftime(c.config["backup"]["backup_time_format"].replace(" ", "_")))

        if args.debug:
            print(" Destination file %s" % (dest_file))

        if os.path.isfile(dest_file):
            if not args.force:
                print("File %s already exists" % (dest_file), file=sys.stderr)
                return_code += 1
                continue
            else:
                print("File %s already exists - will be overwritten" % (dest_file))
                os.remove(dest_file)

        # Purge old files, if applicable
        if retention_period > 0:
            if args.debug:
                print(" Purging files older than %.2f days in the folder %s" % (retention_period, destination))

            now = time.time()
            for f in os.listdir(destination):
                if not f.endswith(".tar.gz"):
                    continue

                f = os.path.join(destination, f)
                if os.path.isfile(f):
                    if os.stat(f).st_mtime < now - (retention_period * 86400):
                        if args.debug:
                            print("   deleting backup %s" % (f))
                        os.remove(f)

        # Initiate export
        status = gitlab.project_export(project, max_tries_number)

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
        if project != export_projects[-1]:
            if args.debug:
                print("Waiting between exports for %d seconds" % (wait_between_exports))
            time.sleep(wait_between_exports)

    sys.exit(return_code)
