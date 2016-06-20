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
module: caas_nat
short_description: "Create, Configure, Remove Network Address Translation on Dimension Data Managed Cloud Platform"
version_added: "1.9"
author: "Olivier GROSJEANNE, @job-so"
description: 
  - "Create, Configure, Remove Network Network Network Address Translation on Dimension Data Managed Cloud Platform"
notes:
  - "This is a wrappper of Dimension Data CaaS API v2.3. Please refer to this documentation for more details and examples : U(https://community.opsourcecloud.net/DocumentRevision.jsp?docId=7897c5018f9bca01cf2f4724de2bcfc5)"
requirements:
    - a caas_credentials variable, see caas_credentials module.  
    - a network domain already deployed, see caas_networkdomain module.
options: 
  caas_credentials: 
    description: 
      - Complexe variable containing credentials. From an external file or from module caas_credentials (See related documentation)
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
  wait:
    description:
      - "Does the task must wait for the vlan creation ? or deploy it asynchronously ?"
    choices: [true,false]
    default: true
  networkDomainId:
    description:
      - "The id of a Network Domain belonging within the same MCP 2.0 data center."
      - "You can use either networkDomainId or networkDomainName, however one of them must be specified"
    default: null
  networkDomainName:
    description:
      - "The name of a Network Domain belonging within the same MCP 2.0 data center."
      - "You can use either networkDomainId or networkDomainName, however one of them must be specified"
    default: null
  internalIp:
    description:
      - "Dot-decimal IPv4 address. For example: "10.11.12.13".
    default: null
    required: true
  externalIp:
    description:
      - "Dot-decimal IPv4 address. For example: "165.180.12.12". Maybe private or public.
      - "If not provided on the request, an unreserved Public IPv4 address from the Public IPv4 Address Blocks belonging Network Domain will be automatically assigned. You can use either networkDomainId or networkDomainName, however one of them must be specified"
    default: null
'''

EXAMPLES = '''
# Create a new private Network Address Translation Rule in network domain "ansible.Caas_SandBox", 
      - name: Deploy a private NAT
        caas_nat:
          #state: absent
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "ansible.Caas_SandBox"
          internalIp: 172.18.1.20
          externalIp: 192.168.110.1
          register: caas_nat

# Delete a Network Address Translation Rule
      - name: Deploy a private NAT
        caas_nat:
          state: absent
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "ansible.Caas_SandBox"
          internalIp: 172.18.1.20
'''

RETURN = '''
        "vlans": 
            type: Dictionary
            returned: success
            description: A list of VLANs (should be one) matching the task parameters.
            sample: 
                "pageCount": 1
                "pageNumber": 1
                "pageSize": 250
                "totalCount": 1
                "vlan":
                  - "createTime": "2016-01-28T08:49:04.000Z"
                    "datacenterId": "EU6"
                    "description": "Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS"
                    "id": "3a454c87-c8f6-4517-8531-b55f9440449c"
                    "ipv4GatewayAddress": "192.168.30.1"
                    "ipv6GatewayAddress": "2a00:47c0:111:1168:0:0:0:1"
                    "ipv6Range":
                        "address": "2a00:47c0:111:1168:0:0:0:0"
                        "prefixSize": 64
                    "name": "ansible.CaaS_Sandbox_vlan_webservers"
                    "networkDomain":
                        "id": "94e50925-2d2f-4727-b137-6d70ce416829"
                        "name": "ansible.CaaS_Sandbox"
                    "privateIpv4Range":
                        "address": "192.168.30.0"
                        "prefixSize": 24
                    "state": "NORMAL"
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
    else: module.fail_json(msg=info['msg'])

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
                if 'body' in info: # ansible version >= 2.1
                    msg = json.loads(info['body'])
                    if msg['responseCode'] == "RESOURCE_BUSY":
                        logging.debug("RESOURCE_BUSY "+str(retryCount)+"/30")
                        time.sleep(10)
                        retryCount += 1
                    else:
                        module.fail_json(msg=msg)
                else:
                    logging.debug("RESOURCE_BUSY ?"+str(retryCount)+"/30")
                    time.sleep(10)
                retryCount += 1
            else:
                module.fail_json(msg=info['msg'])

def _listNatRule(module,caas_credentials,orgId,wait):
    f = { 'internalIp' : module.params['internalIp'], 'networkDomainId' : module.params['networkDomainId']}
    uri = '/caas/2.3/'+orgId+'/network/natRule?'+urllib.urlencode(f)
    result = caasAPI(module,caas_credentials, uri, '')
    return result

def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec = dict(
            caas_credentials = dict(type='dict',required=True,no_log=True),
            state = dict(default='present', choices=['present', 'absent']),
            wait = dict(default=True),
            networkDomainId = dict(default=None),
            networkDomainName = dict(default=None),
            internalIp = dict(default=None,required=True),
            externalIp = dict(default=None),
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False
    
    # Check Authentication and get OrgId
    caas_credentials = module.params['caas_credentials']
    module.params['datacenterId'] = module.params['caas_credentials']['datacenter']

    state = module.params['state']
    wait = module.params['wait']

    orgId = _getOrgId(module,caas_credentials)

    if module.params['networkDomainId']==None:
        if module.params['networkDomainName']!=None:
            f = { 'name' : module.params['networkDomainName'], 'datacenterId' : module.params['datacenterId']}
            uri = '/caas/2.3/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
            result = caasAPI(module,caas_credentials, uri, '')
            if result['totalCount']==1:
                module.params['networkDomainId'] = result['networkDomain'][0]['id']
    
    natRuleList = _listNatRule(module,caas_credentials,orgId,True)
#ABSENT
    if state == 'absent':
        if natRuleList['totalCount'] == 1:
            uri = '/caas/2.3/'+orgId+'/network/deleteNatRule'
            _data = {}
            _data['id'] = natRuleList['natRule'][0]['id']
            data = json.dumps(_data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True

#PRESENT
    if state == "present":
        if natRuleList['totalCount'] < 1:
            uri = '/caas/2.3/'+orgId+'/network/createNatRule'
            _data = {}
            _data['networkDomainId'] = module.params['networkDomainId']
            _data['internalIp'] = module.params['internalIp']
            _data['externalIp'] = module.params['externalIp']
            data = json.dumps(_data)
            print (data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True
    
    natRuleList = _listNatRule(module,caas_credentials,orgId,True)
    module.exit_json(changed=has_changed, natRules=natRuleList)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == '__main__':
    main()
