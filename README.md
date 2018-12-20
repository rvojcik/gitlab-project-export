# gitlab-project-export
Simple python project for exporting gitlab projects with Export Project feature in GitLab API.

Primary used for remote backup of projects in GitLab.com to private storage server.

## Prerequisite
* Python Requests library, `sudo pip install requests`
* Configured Gitlab API Token, https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

## Install

Simple just clone the project.

`git clone https://github.com/rvojcik/gitlab-project-export`

Prepare and edit your config file

`mv config.yaml-example config.yaml`

Simply run the script with optional config parameter

`./gitlab-project-export.py -c /path/to/config.yaml`

