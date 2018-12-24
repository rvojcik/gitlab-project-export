from __future__ import print_function
import requests
import urllib
import sys
import time
import os

class Api:
    '''Api class for gitlab'''

    def __init__(self,gitlab_url, token):
        '''Init config object'''
        self.headers = { "PRIVATE-TOKEN": token }
        self.api_url = gitlab_url + "/api/v4"
        self.download_url = None

    def __api_export(self, project_url):
        '''Send export request to API'''
        self.download_url = None
        return requests.post(self.api_url+"/projects/" + project_url + "/export", headers=self.headers)

    def __api_import(self, project_name, namespace, filename):
        '''Send import request to API'''
        data = { "path": project_name, "namespace": namespace, "overwrite": True}
        return requests.post(self.api_url+"/projects/import", data=data, files={"file": open(filename, 'r')}, headers=self.headers)

    def __api_status(self,project_url):
        '''Check project status'''
        return requests.get(self.api_url+"/projects/" + project_url + "/export", headers=self.headers)

    def __api_import_status(self,project_url):
        '''Check project import status'''
        return requests.get(self.api_url+"/projects/" + project_url + "/import", headers=self.headers)

    def project_export(self, project_path):
        ''' Export Gitlab project
        When project export is finished, store download URLs 
        in objects variable download_url ready to be downloaded'''

        url_project_path = urllib.quote(project_path, safe='')
        
        # Let's export project
        r = self.__api_export(url_project_path)
        if ( (float(r.status_code) >= 200) and (float(r.status_code) < 300) ):
            # Api good, check for status
            max_tries = 20
            s = ""
            status_export = False
            while max_tries != 0:
                # Decrement tries
                max_tries -= 1

                r = self.__api_status(url_project_path)

                # Check API reply status
                if ( r.status_code == requests.codes.ok ):
                    json = r.json()

                    # Check export status
                    if "export_status" in json.keys():
                        s = json["export_status"]
                        if s == "finished":
                            status_export = True
                            break
                    else:
                        s = "unknown"
                    
                else:
                    print("API not respond well with %s" %(str(r.status_code)), file=sys.stderr)
                    break

                # Wait litle bit
                time.sleep(2)

            if status_export:
                self.download_url = json["_links"]
                return True
            else:
                return False
                    
        else:
            print("API not respond well with %s" %(str(r.status_code)), file=sys.stderr) 
            print(r.text, file=sys.stderr)
            return False

    def project_import(self, project_path, filepath):
        ''' Import project to GitLab from file'''
        url_project_path = urllib.quote(project_path, safe='')
        project_name = os.path.basename(project_path)
        namespace = os.path.dirname(project_path)
        
        # Let's import project
        r = self.__api_import(project_name, namespace, filepath)
        if ( (float(r.status_code) >= 200) and (float(r.status_code) < 300) ):
            # Api good, check for status
            s = ""
            status_export = False
            while True:
                r = self.__api_import_status(url_project_path)

                # Check API reply status
                if ( r.status_code == requests.codes.ok ):
                    json = r.json()

                    # Check export status
                    if "import_status" in json.keys():
                        s = json["import_status"]
                        if s == "finished":
                            status_import = True
                            break
                        elif s == "failed":
                            status_import = False
                            break
                    else:
                        s = "unknown"
                    
                else:
                    print("API not respond well with %s" %(str(r.status_code)), file=sys.stderr)
                    break

                # Wait litle bit
                time.sleep(2)

            if status_import:
                return True
            else:
                return False
                    
        else:
            print("API not respond well with %s" %(str(r.status_code)), file=sys.stderr) 
            print(r.text, file=sys.stderr)
            return False
