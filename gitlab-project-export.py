#!/usr/bin/env python

from __future__ import print_function
import sys
import os
import argparse
import yaml
from lib import config, gitlab
from datetime import date
import requests

return_code = 0

if __name__ == '__main__':
    # Parsing arguments
    parser = argparse.ArgumentParser(
        description= 'GitLab project Export', 
        epilog='Created by Robert Vojcik <robert@vojcik.net>')
    
    # Arguments
    parser.add_argument('-c', dest='config', default='config.yaml',
                       help='sum the integers (default: find the max)') 
    
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print("Unable to find config file %s" % (args.config)) 

    c = config.Config(args.config)
    token = c.config["gitlab"]["access"]["token"]
    gitlab_url = c.config["gitlab"]["access"]["gitlab_url"]

    # Init gitlab api object
    gitlab = gitlab.Api(gitlab_url, token)

    # Export each project
    for project in c.config["gitlab"]["projects"]:
        status = gitlab.project_export(project)

        # Export successful
        if status:
            # Download project to our destination
            if c.config["backup"]["project_dirs"]:
                destination = c.config["backup"]["destination"] + "/" + project 
            else:
                destination = c.config["backup"]["destination"]

            # Prepare actual date
            d = date.today()
            # File template from config
            file_tmpl = c.config["backup"]["backup_name"]
            # Projectname in dest_file
            dest_file = destination + "/" + file_tmpl.replace("{PROJECT_NAME}", project.replace("/", "-"))
            # Date in dest_file
            dest_file = dest_file.replace("{TIME}",d.strftime(c.config["backup"]["backup_time_format"]))

            # Create directories
            if not os.path.isdir(destination):
                os.makedirs(destination)

            # Get URL from gitlab object
            url = gitlab.download_url["api_url"]

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
