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

## Configuration
System uses simple yaml file as configuration.

Example below
```
gitlab:                                                   - gitlab configuration
  access:
    gitlab_url: "https://gitlab.com"                      - Gitlab url, official or your instance
    token: "MY_PERSONAL_SECRET_TOKEN"                     - personal access token
  projects:                                               - list of projects to export
    - rvojcik/example-project

backup:                                                   - backup configuration
  project_dirs: True                                      - store projects in separate directories
  destination: "/data/backup"                             - base backup dir
  backup_name: "gitlab-com-{PROJECT_NAME}-{TIME}.tar.gz"  - backup file template
  backup_time_format: "%Y%m%d"                            - TIME tamplate, use whatever compatible with
                                                            python datetime - date.strftime()
  ```
  

### Backup Usecase in cron

Create cron file in `/etc/cron.d/gitlab-backup`

With following content
```
MAILTO=your_email@here.tld

0 1 * * * root /path/to/cloned-repo/gitlab-project-export.py -c /etc/gitlab-export/config.yaml

```
