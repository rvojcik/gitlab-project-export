# gitlab-project-export
Simple python project for exporting gitlab projects with Export Project feature in GitLab API.

Primary used for remote backup of projects in GitLab.com to private storage server.

## Breaking Changes 
### 05-2020
Code was modified to work with Python3, not longer compatible with Python2.

## Prerequisite
* Configured Gitlab API Token, https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

## Install

Simply install via pip:

`pip install git+https://github.com/rvojcik/gitlab-project-export`

or clone the project and install dependecies manually:

```
git clone https://github.com/rvojcik/gitlab-project-export
pip install pyyaml
pip install requests
```

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

### Migration Usecase
First create two config files

config1.yaml for exporting our project from gitlab.com
```
gitlab:                                                   - gitlab configuration
  access:
    gitlab_url: "https://gitlab.com"                      - Gitlab url, official or your instance
    token: "MY_PERSONAL_SECRET_TOKEN"                     - personal access token
  projects:                                               - list of projects to export
    - rvojcik/project1
    - rvojcik/project2

backup:                                                   - backup configuration
  project_dirs: False                                     - store projects in separate directories
  destination: "/data/export-dir"                             - base backup dir
  backup_name: "gitlab-com-{PROJECT_NAME}-{TIME}.tar.gz"  - backup file template
  backup_time_format: "%Y%m%d"                            - TIME tamplate, use whatever compatible with
                                                            python datetime - date.strftime()
```

and config2.yaml where we need only gitlab access part for importing projects to private gitlab instance
```
gitlab:                                                   - gitlab configuration
  access:
    gitlab_url: "https://gitlab.privatedomain.tld"        - Gitlab url, official or your instance
    token: "MY_PERSONAL_SECRET_TOKEN"                     - personal access token
```

Now it's time to export our projects
```
./gitlab-project-export.py -c ./config1.yaml -d
```
Your projects are now exported in `/data/export-dir`

After that we use `gitlab-project-import.py` with config2.yaml for importing into our pricate gitlab instance.

```
./gitlab-project-import.py -c ./config2.yaml -f ./gitlab-com-rvojcik-project1-20181224.tar.gz -p "rvojcik/project1"
./gitlab-project-import.py -c ./config2.yaml -f ./gitlab-com-rvojcik-project2-20181224.tar.gz -p "rvojcik/project2"
```

Done ;)
