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
    import xml.etree.ElementTree as ET
    IMPORT_STATUS = True
except ImportError:
    IMPORT_STATUS = False

DOCUMENTATION = '''
--- 
module: caas_networkdomain
author: "Olivier GROSJEANNE, @job-so"
short_description: "Create, Configure, Remove Network Domains on Dimension Data Managed Cloud Platform"
version_added: "1.9"
description: 
  - "Create, configure, Remove Network Domains on Dimension Data Managed Cloud Platform"
notes:
  - "This is a wrappper of Dimension Data CaaS API v2.1. Please refer to this documentation for more details and examples : U(https://community.opsourcecloud.net/DocumentRevision.jsp?docId=7897c5018f9bca01cf2f4724de2bcfc5)"
requirements:
    - a caas_credentials variable, see caas_credentials module.  
options: 
  caas_credentials: 
    description: 
      - Complexe variable containing credentials. From an external file or from module caas_credentials (See related documentation)
    required: true
  name: 
    description: 
      - "Name that has to be given to the instance"
      - "Minimum length 1 character Maximum length 75 characters."
    required: true
  state:  
    choices: ['present','absent']
    default: present
    description: 
      - "Should the resource be present or absent."
      - "Take care : Absent will delete the networkdomain"
  description:
    description:
      - "Maximum length: 255 characters."
    default: "Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS"
  type:
    description:
      - "Type of the network domain, ADVANCED features include Load Balancing capabilities."
    default: "ESSENTIALS"
    choices: ['ESSENTIALS', 'ADVANCED']
'''

EXAMPLES = '''
# Create a new networkdomain named "ansible.Caas_SandBox", 
    tasks:
      - name: Deploy my Nework Domain
        caas_networkdomain:
          caas_credentials: "{{ caas_credentials }}"
          name: ansible.CaaS_Sandbox
          type: ADVANCED
        register: caas_networkdomain
'''

RETURN = '''
        "networkdomains":
            type: Dictionary
            returned: success
            description: A list of networkDomain (should be one) matching the task parameters.
            sample: 
                "networkDomain":
                  - "createTime": "2016-01-26T16:26:21.000Z"
                    "datacenterId": "EU6"
                    "description": "Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS"
                    "id": "4dc7c62c-d2c1-447d-a5de-9a18a9e14c5c"
                    "name": "ansible.CaaS_Sandbox"
                    "snatIpv4Address": "168.128.10.72"
                    "state": "NORMAL"
                    "type": "ADVANCED"
                "pageCount": 1
                "pageNumber": 1
                "pageSize": 250
                "totalCount": 1
...
'''
logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_networkdomain---"+str(datetime.datetime.now()))

def _getOrgId(module, caas_credentials):
    apiuri = '/oec/0.9/myaccount'
    url = caas_credentials['apiurl'] + apiuri
    base64string = base64.encodestring('%s:%s' % (caas_credentials['username'], caas_credentials['password'])).replace('\n', '')
    headers = { "Authorization": "Basic %s" % (base64string) }
    response, info = fetch_url(module, url, headers=headers) 
    if info['status'] == 200:
        root = ET.fromstring(response.read())
        ns = {'directory': 'http://oec.api.opsource.net/schemas/directory'}
        return root.find('directory:orgId',ns).text
    else:
	    module.fail_json(msg=info['msg'])

def caasAPI(module, caas_credentials, apiuri, data):
    logging.debug(apiuri)
    url = caas_credentials['apiurl'] + apiuri
    base64string = base64.encodestring('%s:%s' % (caas_credentials['username'], caas_credentials['password'])).replace('\n', '')
    headers = { "Authorization": "Basic %s" % (base64string), "Content-Type": "application/json"}
    retryCount = 0
    while retryCount < 5*6:
        if data == '': response, info = fetch_url(module, url, headers=headers) 
        else: response, info = fetch_url(module, url, headers=headers, data=data) 
        if info['status'] == 200: return json.loads(response.read())
        else:
            if info['status'] == 400:
                msg = json.loads(response.read())
                if msg['responseCode'] == "RESOURCE_BUSY":
                    logging.debug("RESOURCE_BUSY "+str(retryCount)+"/30")
                    time.sleep(10)
                    retryCount += 1
                else:
                    module.fail_json(msg=msg)
            else:
                module.fail_json(msg=info['msg'])

def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec = dict(
            caas_credentials = dict(type='dict',required=True,no_log=True),
            state = dict(default='present', choices=['present', 'absent']),
            name = dict(required=True),
            description = dict(default='Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS'),
            type = dict(default='ESSENTIALS', choices=['ESSENTIALS', 'ADVANCED'])
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False
    
    # Check Authentication and get OrgId
    caas_credentials = module.params['caas_credentials']
    module.params['datacenterId'] = module.params['caas_credentials']['datacenter']
    state = module.params['state']

    orgId = _getOrgId(module, caas_credentials)

    f = { 'name' : module.params['name'], 'datacenterId' : module.params['datacenterId']}
    uri = '/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
    networkDomainList = caasAPI(module,caas_credentials, uri, '')
     
#ABSENT
    if state == 'absent':
        if networkDomainList['totalCount'] == 1:
            uri = '/caas/2.1/'+orgId+'/network/deleteNetworkDomain'
            _data = {}
            _data['id'] = networkDomainList['networkDomain'][0]['id']
            data = json.dumps(_data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True
#PRESENT
    if state == "present":
        if networkDomainList['totalCount'] < 1:
            uri = '/caas/2.1/'+orgId+'/network/deployNetworkDomain'
            _data = {}
            _data['datacenterId'] = module.params['caas_credentials']['datacenter']
            _data['name'] = module.params['name']
            _data['description'] = module.params['description']
            _data['type'] = module.params['type']
            data = json.dumps(_data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True
    
    f = { 'name' : module.params['name'], 'datacenterId' : module.params['datacenterId']}
    uri = '/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
    networkDomainList = caasAPI(module,caas_credentials, uri, '')
    module.exit_json(changed=has_changed, networkdomains=networkDomainList)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == '__main__':
    main()
