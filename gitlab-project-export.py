#!/usr/bin/env python

from __future__ import print_function
import sys
import os
import argparse
import yaml
from datetime import date
import requests
# Find our libs
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from lib import config, gitlab


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
    parser.add_argument('-c', dest='config', default='config.yaml',
                       help='config file')
    parser.add_argument('-d', dest='debug', default=False, action='store_const', const=True,
                       help='Debug mode')

    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print("Unable to find config file %s" % (args.config))

    c = config.Config(args.config)
    token = c.config["gitlab"]["access"]["token"]
    gitlab_url = c.config["gitlab"]["access"]["gitlab_url"]

    # Init gitlab api object
    if args.debug:
        print("%s, token"%(gitlab_url))
    gitlab = gitlab.Api(gitlab_url, token)

    # Export each project
    for project in c.config["gitlab"]["projects"]:
        if args.debug:
            print("Exporting %s"%(project))
        status = gitlab.project_export(project)

        # Export successful
        if status:
            if args.debug:
                print("Success for %s"%(project))
            # Download project to our destination
            if c.config["backup"]["project_dirs"]:
                destination = c.config["backup"]["destination"] + "/" + project
            else:
                destination = c.config["backup"]["destination"]

            if args.debug:
                print(" Destination %s"%(destination))

            # Prepare actual date
            d = date.today()
            # File template from config
            file_tmpl = c.config["backup"]["backup_name"]
            # Projectname in dest_file
            dest_file = destination + "/" + file_tmpl.replace("{PROJECT_NAME}", project.replace("/", "-"))
            # Date in dest_file
            dest_file = dest_file.replace("{TIME}",d.strftime(c.config["backup"]["backup_time_format"]))

            if args.debug:
                print(" Destination file %s"%(dest_file))

            # Create directories
            if not os.path.isdir(destination):
                os.makedirs(destination)

            # Get URL from gitlab object
            url = gitlab.download_url["api_url"]
            if args.debug:
                print(" URL: %s"%(url))

            # Download file
            r = requests.get(url, allow_redirects=True, stream=True, headers={"PRIVATE-TOKEN": token})

            with open(dest_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        else:
            # Export for project unsuccessful
            print("Export failed for project %s" % (project), file=sys.stderr)
            return_code += 1

    sys.exit(return_code)
