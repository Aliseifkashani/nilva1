#!/usr/bin/env python

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import json
from googleapiclient.errors import HttpError
from googleapiclient.errors import UnknownApiNameOrVersion
import sys
import time

import googleapiclient

from googleapiclient.errors import HttpError
import requests
import httplib2

from httplib2 import ServerNotFoundError

try:
    from urllib import urlencode, unquote
    from urlparse import urlparse, parse_qsl, ParseResult
except ImportError:
    from urllib.parse import (
        urlencode, unquote, urlparse, parse_qsl, ParseResult
    )



class GoogleClient:

    def __init__(self, key_file_location,scopes):
        self.key_file_location = key_file_location
        self.scopes = scopes
        with open(key_file_location) as json_file:  
            data = json.load(json_file)
            self.project_id = data['project_id']

        self.compute = self.get_service(
            api_name='compute',
            api_version='v1',
            scopes=['https://www.googleapis.com/auth/compute'] )



    def to_err_message(self,err):
    
     return err.message if hasattr(err, 'message') else str(err)

    def to_err_code(self,err):
        
        return err.code if hasattr(err, 'code') else 0

    def wait_for_operation(self,  operation,opreationType,RegionOrZone ):
        global compute
        params={'project':self.project_id, 'operation':operation}

        opreationType=opreationType
        if opreationType=='zone':
            params['zone']= RegionOrZone
            opreationType='zoneOperations'
        else:
            params['region']= RegionOrZone
            opreationType='regionOperations'

          
           

     
        
        #print('Polling...')
        while True:
            response= self.exec_func(self.compute,opreationType,'get',params)
            
            if not response['status']:
                return response['message']
            elif response['result']['status'] == 'DONE':
                if 'error' in response['result']:
                    return response['error']
                else:
                    print("Progress: " + str(response['result']['progress']) +"%")
                    res= self.authinticated_http_call(response['result']['targetLink'])
                    if not res['status']:
                        return res['message']
                    else:
                        return res['result']
            else:
                print("Progress: " + str(response['result']['progress']) +"%")                
             
            time.sleep(1)

    def wait_for_zone_operation(   zone, operation):
        return self.wait_for_operation( operation,opreationType='zone',RegionOrZone=zone)       

    def exec_func(self, service ,item,fn,params):
        try:
            if not('project' in params):
                params['project']=self.project_id

            if not(fn=="get" and (item=='zoneOperations' or item=='regionOperations')):    
                print("Executing: " +fn)

            if not type(service) == googleapiclient.discovery.Resource:
                print(type(service))
                raise Exception('Invalid service Object: '+service ) # Don't! If you catch, likely to hide bugs.

            res=getattr(service, item)(); 
            res=getattr(res, fn)(**params);
            serviceResult=res.execute()

            if fn=="get" and (item=='zoneOperations' or item=='regionOperations'):
               return {'status':1,'result':serviceResult}    

             
            
            if 'kind' in serviceResult and '#operation' in  serviceResult['kind']:

                if '/regions/' in  serviceResult['selfLink']:
                    splt= serviceResult['region'].split("/")
                    opreationType="region"
                else:
                    #print(serviceResult['zone'])
                    splt= serviceResult['zone'].split("/")
                    opreationType="zone"

                #print(splt)    



                
                result= self.wait_for_operation(  operation=serviceResult['name'],opreationType=opreationType,RegionOrZone=splt[-1])
                if not result:
                    raise Exception(result )
                else:
                    serviceResult= result
                    
                            



            
            return {'status':1,'result':serviceResult}            
        

                     
                
      
         
        except HttpError as err:
            return {'status':0,'message':self.to_err_message(err),'code':self.to_err_code(err),'error':err}
        except UnknownApiNameOrVersion as err:
            return {'status':0,'message':self.to_err_message(err),'code':self.to_err_code(err),'error':err}
        except Exception as err:
            return {'status':0,'message':self.to_err_message(err),'code':self.to_err_code(err),'error':err}

     
            

    def authinticated_http_call(self,url,scopes=[]):
        try:
            credentials = self.make_credentials(scopes )
            http = httplib2.Http()
            http = credentials.authorize(http)

            url=self.add_url_params(url,{'alt':'json'})
            
            resp, content=http.request(url, "GET")

            result = json.loads( content.decode('utf-8'))
            if 'error' in result:
               raise Exception(result['error']['errors'][0]['message'])

            return {'status':1,'result':result}
            
        except ServerNotFoundError as err:
            return {'status':0,'message':self.to_err_message(err),'code':self.to_err_code(err),'error':err}
        except Exception as err:
            return {'status':0,'message':self.to_err_message(err),'code':self.to_err_code(err),'error':err}    

    def make_credentials(self,scopes=[] ):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.key_file_location, scopes=self.scopes if len(scopes)==0 else scopes )
        return credentials


    def get_service(self,api_name, api_version, scopes=[]):
        

        credentials = self.make_credentials(scopes)
         

        try:
            service = build(api_name, api_version, credentials=credentials)

        except UnknownApiNameOrVersion as err:
            return self.to_err_message(err)
        except Exception as err:
            return self.to_err_message(err)


        return service

    
    def add_url_params(self,url, params):
    
        url = unquote(url)
        parsed_url = urlparse(url)
        get_args = parsed_url.query
        parsed_get_args = dict(parse_qsl(get_args))
        parsed_get_args.update(params)

        
        parsed_get_args.update(
            {k: dumps(v) for k, v in parsed_get_args.items()
             if isinstance(v, (bool, dict))}
        )

        encoded_get_args = urlencode(parsed_get_args, doseq=True)
        new_url = ParseResult(
            parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            parsed_url.params, encoded_get_args, parsed_url.fragment
        ).geturl()

        return new_url    


