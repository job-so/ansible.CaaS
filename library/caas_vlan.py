#!/usr/bin/python
# coding: utf-8 -*-

# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

try:
    import datetime
    import json
    import logging
    import base64
    import urllib
    import urllib2
    import xml.etree.ElementTree as ET
    IMPORT_STATUS = True
except ImportError:
    IMPORT_STATUS = False

DOCUMENTATION = '''
--- 
author: "Olivier GROSJEANNE, @job-so"
description: 
  - "Create, Remove Network vlans on Dimension Data Managed Cloud Platform"
module: caas_vlan
options: 
  caas_apiurl: 
    description: 
      - See caas_server for more information
    required: true
  caas_datacenter: 
    description: 
      - See caas_server for more information
    required: true
  caas_password: 
    description: 
      - "The associated password"
    required: true
  caas_username: 
    description: 
      - "Your username credential"
    required: true
  name: 
    description: 
      - "Name that has to be given to the instance"
      - "The name must be unique inside the DataCenter"
      - "Minimum length 1 character Maximum length 75 characters."
    required: true
  state:  
    choices: ['present','absent']
    default: present
    description: 
      - "Should the resource be present or absent."
      - "Take care : Absent will powerOff and delete all servers."
  description:
    description:
      - "Maximum length: 255 characters."
    default: "Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS"
  networkDomainId:
    description:
      - "The id of a Network Domain belonging to {org-id} within the same MCP 2.0 data center."
    default: null
  networkDomainName:
    description:
      - "The name of a Network Domain belonging to {org-id} within the same MCP 2.0 data center."
    default: null
  privateIpv4BaseAddress:
    description:
      - "RFC1918 Dot-decimal representation of an IPv4 address."
      - "For example: “10.0.4.0”. Must be unique within the Network Domain."
    default: null
  privateIpv4BaseAddress:
    description:
      - "An Integer between 16 and 24, which represents the size of the VLAN to be deployed and must be consistent with the privateIpv4BaseAddress provided."
      - "If this property is not provided, the VLAN will default to being /24"
    default: null
short_description: "Create, Configure, Remove Network Domain on Dimension Data Managed Cloud Platform"
version_added: "1.9"
'''

EXAMPLES = '''
# Creates a new vlan named "ansible.Caas_SandBox", 
-caas_networkdomain:
    caas_apiurl: "{{ caas_apiurl }}"
    caas_username: "{{ caas_username }}"
    caas_password: "{{ caas_password }}"
    datacenterId: "{{ caas_datacenter }}"
    name: "vlan_webservers"
    register: caas_networkdomain
'''

logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_networkdomain---"+str(datetime.datetime.now()))

def _getOrgId(username, password, apiurl):
    apiuri = '/oec/0.9/myaccount'
    request = urllib2.Request(apiurl + apiuri)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    result = {}
    result['status'] = False
    try:
        response = urllib2.urlopen(request).read()
        root = ET.fromstring(response)
        ns = {'directory': 'http://oec.api.opsource.net/schemas/directory'}
        result['orgId'] = root.find('directory:orgId',ns).text
        result['status'] = True
    except urllib2.URLError as e:
        result['msg'] = e.reason
    except urllib2.HTTPError, e:
        result['msg'] = e.read()
    return result

def _listVlan(module,caas_username,caas_password,caas_apiurl,orgId,wait):
    f = { 'name' : module.params['name'], 'networkDomainId' : module.params['networkDomainId']}
    uri = caas_apiurl+'/caas/2.1/'+orgId+'/network/vlan?'+urllib.urlencode(f)
    b = True;
    while wait and b:
        result = caasAPI(caas_username,caas_password, uri, '')
        vlanList = result['msg']
        b = False
        for (vlan) in vlanList['vlan']:
            logging.debug(vlan['id']+' '+vlan['name']+' '+vlan['state'])
            if vlan['state'] != "NORMAL":
		        b = True
        if b:
            time.sleep(5)
    return vlanList

def caasAPI(username, password, uri, data):
    logging.debug(uri)
    if data == '':
        request = urllib2.Request(uri)
    else:
        request	= urllib2.Request(uri, data)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    request.add_header("Content-Type", "application/json")
    result = {}
    result['status'] = False
    retryCount = 0
    while (result['status'] == False) and (retryCount < 5*6):
        try:
            response = urllib2.urlopen(request)
            result['msg'] = json.loads(response.read())
            result['status'] = True
        except urllib2.HTTPError, e:
            if e.code == 400:
                result['msg'] = json.loads(e.read())
                if result['msg']['responseCode'] == "RESOURCE_BUSY":
                    logging.debug("RESOURCE_BUSY "+str(retryCount)+"/30")
                    time.sleep(10)
                    retryCount += 1
                else:
                    retryCount = 9999
            else:
                retryCount = 9999
                result['msg'] = str(e.code) + e.reason + e.read()
        except urllib2.URLError as e:
            result['msg'] = str(e.code)
            retryCount = 9999
    return result

def main():
    module = AnsibleModule(
        argument_spec = dict(
            caas_apiurl = dict(required=True),
            datacenterId = dict(required=True),
            caas_username = dict(required=True),
            caas_password = dict(required=True,no_log=True),
            state = dict(default='present', choices=['present', 'absent']),
            wait = dict(default=True),
            name = dict(required=True),
            description = dict(default='Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS'),
            networkDomainId = dict(default=None),
            networkDomainName = dict(default=None),
            privateIpv4BaseAddress = dict(default=None),
            privateIpv4PrefixSize = dict(default=None),
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False
	
    # Check Authentication and get OrgId
    caas_username = module.params['caas_username']
    module.params.pop('caas_username', None)
    caas_password = module.params['caas_password']
    module.params.pop('caas_password', None)
    caas_apiurl = module.params['caas_apiurl']
    module.params.pop('caas_apiurl', None)

    state = module.params['state']
    module.params.pop('state', None)

    wait = module.params['wait']
    module.params.pop('wait', None)

    result = _getOrgId(caas_username,caas_password,caas_apiurl)
    if not result['status']:
        module.fail_json(msg=result['msg'])
    orgId = result['orgId']

	#Check dataCenterId
    #if not datacenterId
	
    if module.params['networkDomainId']==None:
        if module.params['networkDomainName']!=None:
            f = { 'name' : module.params['networkDomainName'], 'datacenterId' : module.params['datacenterId']}
            uri = caas_apiurl+'/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
            result = caasAPI(caas_username,caas_password, uri, '')
            if result['status']:
                if result['msg']['totalCount']==1:
                    module.params['networkDomainId'] = result['msg']['networkDomain'][0]['id']
                    module.params.pop('networkDomainName', None)
                    module.params.pop('datacenterId', None)					
	
    vlanList = _listVlan(module,caas_username,caas_password,caas_apiurl,orgId,True)
 	
   # if state=absent
    #if state=='absent':
        #nothing
	
	# if state=present
    if state == "present":
        if vlanList['totalCount'] < 1:
            uri = caas_apiurl+'/caas/2.1/'+orgId+'/network/deployVlan'
            data = json.dumps(module.params)
            result = caasAPI(caas_username,caas_password, uri, data)
            if not result['status']:
                module.fail_json(msg=result['msg'])
            else:
                has_changed = True
	
    vlanList = _listVlan(module,caas_username,caas_password,caas_apiurl,orgId,wait)
    module.exit_json(changed=has_changed, networkdomain=vlanList)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
