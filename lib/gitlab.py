from __future__ import print_function
import requests
import urllib
import sys
import time

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

    def __api_status(self,project_url):
        '''Check project status'''
        return requests.get(self.api_url+"/projects/" + project_url + "/export", headers=self.headers)

    def project_export(self, project_path):
        url_project_path = urllib.quote(project_path, safe='')
        
        # Let's export project
        r = self.__api_export(url_project_path)
        if ( str(r.status_code) == "202" ):
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
                    print(json)
                    if "export_status" in json.keys():
                        s = json["export_status"]
                        if s == "finished":
                            status_export = True
                            break
                    else:
                        s = "unknown"
                    print(s)
                    
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
            return False

