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
module: caas_loadbalancer
author: "Olivier GROSJEANNE, @job-so"
description: 
  - "Create, Configure, Remove LoadBalancer instances on Dimension Data Managed Cloud Platform"
short_description: "Create, Configure, Remove Load Balancer instances on Dimension Data Managed Cloud Platform"
version_added: "1.9"
notes:
  - "This is a wrappper of Dimension Data CaaS API v2.1. Please refer to this documentation for more details and examples : U(https://community.opsourcecloud.net/DocumentRevision.jsp?docId=7897c5018f9bca01cf2f4724de2bcfc5)"
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
      - "Take care : Absent will powerOff and delete all servers."
  description:
    description:
      - "Maximum length: 255 characters."
    default: "Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS"
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
  type:
    choices: ['STANDARD','PERFORMANCE_LAYER_4']
    default: STANDARD
    description: 
      - "Must be one of choices."
  protocol:
    choices: ['ANY','TCP','UDP','HTTP']
    default: TCP
    description: 
      - "The permitted range of values for protocol is governed by the choice of the type property."
      - "For STANDARD type, protocol must be one of: ANY, TCP, UDP"
      - "For PERFORMANCE_LAYER_4 type, protocol must be one of: ANY, TCP, UDP, HTTP"
  listenerIpAddress:
    description:
      - "Must be a valid IPv4 in dot-decimal notation (x.x.x.x)."
      - "listenerIpAddress can be one of two types:"
      - "Public: listenerIpAddress is *optional for creating a Public IP address Virtual Listener. If not supplied, the “Public” type below is assumed, and an available public IP is picked up from public ip blocks. see M(caas_publicip)"
      - "Private: listenerIpAddress is *required to create a Private IP address Virtual Listener."
    default: null
  port:
    description:
      - "An integer in the range 1-65535"
      - "If port is not supplied it will be taken to mean 'Any Port'."
    default: null
  enabled:
    choices: ['True','False']
    default: True
    description: 
      - "Must be one of true or false, where true indicates that the Virtual Listener will permit traffic to flow to its Pool and/or Client Clone Pool."
  connectionLimit:
    default: 25000
    description: 
      - "An integer in the range 1 -MAX_VIRTUAL_LISTENER_CONNECTION_LIMIT. See Data Centers features/property"
  connectionRateLimit:
    default: 2000
    description: 
      - "An integer in the range 1 -MAX_VIRTUAL_LISTENER_CONNECTION_RATE_LIMIT. See Data Centers features/property"
  sourcePortPreservation:
    choices: ['PRESERVE','PRESERVE_STRICT','CHANGE']
    default: PRESERVE
    description: 
      - "Must be one of choices."
  optimizationProfile:
    choices: ['TCP', 'LAN_OPT', 'WAN_OPT', 'MOBILE_OPT', 'TCP_LEGACY', 'SMTP', 'SIP']
    default: TCP
    description: 
      - "An optimizationProfile can only be included for certain type and protocol combinations:"
      - "1. STANDARD/TCP: optimizationProfile is required for this combination and must be one of: TCP, LAN_OPT, WAN_OPT, MOBILE_OPT, TCP_LEGACY."
      - "2. STANDARD/UDP: SMTP or SIP."
  pool.name:
    default: "{{name}}.pool"
    description: 
      - "Must be alphanumeric with the following exceptions permitted '_' (underscore) and '.' (full stop / period)"
  pool.description:
    default: "{{description}}"
    description: 
      - "Maximum length: 255 characters."
  pool.loadBalanceMethod:
    choices: ['ROUND_ROBIN','LEAST_CONNECTIONS_MEMBER','LEAST_CONNECTIONS_NODE','OBSERVED_MEMBER','OBSERVED_NODE','PREDICTIVE_MEMBER','PREDICTIVE_NODE']
    default: ROUND_ROBIN
    description: 
      - "Must be one of choices."
  pool.healthMonitorId:
    default: null
    description: 
      - "NOT IMPLEMENTED"
  pool.serviceDownAction:
    choices: ['NONE', 'DROP', 'RESELECT']
    default: RESELECT
    description: 
      - "Must be one of choices."
  pool.slowRampTime:
    default: 30
    description: 
      - "An integer in the range 1-120 (seconds)."
'''

EXAMPLES = '''
#
'''

logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_loadbalancer---"+str(datetime.datetime.now()))

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
                msg = json.loads(info['body'])
                if msg['responseCode'] == "RESOURCE_BUSY":
                    logging.debug("RESOURCE_BUSY "+str(retryCount)+"/30")
                    time.sleep(10)
                    retryCount += 1
                else:
                    module.fail_json(msg=msg)
            else:
                module.fail_json(msg=info['msg'])

def _listVirtualListenerRule(module,caas_credentials,orgId,wait):
    f = { 'name' : module.params['name'], 'networkDomainId' : module.params['networkDomainId']}
    uri = '/caas/2.1/'+orgId+'/networkDomainVip/virtualListener?'+urllib.urlencode(f)
    b = True;
    while b:
        virtualListenerList = caasAPI(module,caas_credentials, uri, '')
        b = False
        for (virtualListener) in virtualListenerList['virtualListener']:
            logging.debug(firewallRule['id']+' '+firewallRule['name']+' '+firewallRule['state'])
            if (firewallRule['state'] != "NORMAL") and wait:
                b = True
        if b:
            time.sleep(5)
    return firewallRuleList

def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec = dict(
            caas_credentials = dict(type='dict',required=True,no_log=True),
            state = dict(default='present', choices=['present', 'absent']),
            wait = dict(default=True),
            id = dict(default=None),
            name = dict(required=True),
            description = dict(default='Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS'),
            networkDomainName = dict(default=None),
            networkDomainId = dict(default=None),
            type=dict(default='STANDARD', choices = ['STANDARD','PERFORMANCE_LAYER_4']),
            protocol=dict(default='TCP', choices = ['ANY','TCP','UDP','HTTP']),
            listenerIpAddress = dict(default=None),
            port = dict(default=None),
            enabled = dict(type='bool',default=True, choices = [True,False]),
            connectionLimit = dict(type='int',default=25000),
            connectionRateLimit= dict(type='int',default=2000),
            sourcePortPreservation=dict(default='PRESERVE', choices = ['PRESERVE','PRESERVE_STRICT','CHANGE']),
#clientClonePoolId": "033a97dc-ee9b-4808-97ea-50b06624fd16",
#persistenceProfileId": "a34ca25c-f3db-11e4-b010-005056806999"
#fallbackPersistenceProfileId": "6f2f5d7b-cdd9-4d84-8ad7-999b64a87978",
#iruleId": ["2b20abd9-ffdc-11e4-b010-005056806999"],
            optimizationProfile=dict(type='list',default='TCP'), #choices = ['TCP', 'LAN_OPT', 'WAN_OPT', 'MOBILE_OPT', 'TCP_LEGACY', 'SMTP', 'SIP']),
            pool=dict(type='dict',required=False),
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False

    # Check Authentication and get OrgId
    caas_credentials = module.params['caas_credentials']
    module.params['datacenterId'] = module.params['caas_credentials']['datacenter']

    wait = module.params['wait']
    state = module.params['state']

    orgId = _getOrgId(module, caas_credentials)

    if module.params['networkDomainId']==None:
        if module.params['networkDomainName']!=None:
            f = { 'name' : module.params['networkDomainName'], 'datacenterId' : module.params['datacenterId']}
            uri = '/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
            result = caasAPI(module,caas_credentials, uri, '')
            if result['totalCount']==1:
                module.params['networkDomainId'] = result['networkDomain'][0]['id']

    f = { 'name' : module.params['name'], 'datacenterId' : module.params['datacenterId'], 'networkDomainId' : module.params['networkDomainId']}
    uri = '/caas/2.1/'+orgId+'/networkDomainVip/virtualListener?'+urllib.urlencode(f)
    virtualListenerList = caasAPI(module,caas_credentials, uri, '')
 
#ABSENT
    if state == "absent":
        if virtualListenerList['totalCount'] == 1:
            #Delete Virtual Listener
            uri = '/caas/2.1/'+orgId+'/networkDomainVip/deleteVirtualListener'
            _data = {}
            _data['id'] = virtualListenerList['virtualListener'][0]['id']
            data = json.dumps(_data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True
            if virtualListenerList['virtualListener'][0]['pool']['id']!='':
                #List associated Nodes
                f = { 'poolId' : virtualListenerList['virtualListener'][0]['pool']['id'] }
                uri = '/caas/2.1/'+orgId+'/networkDomainVip/poolMember?'+urllib.urlencode(f)
                poolMembers = caasAPI(module,caas_credentials, uri, '')
                #Delete associated Pool
                uri = '/caas/2.1/'+orgId+'/networkDomainVip/deletePool'
                _data = {}
                _data['id'] = virtualListenerList['virtualListener'][0]['pool']['id']
                data = json.dumps(_data)
                if module.check_mode: has_changed=True
                else: 
                    result = caasAPI(module,caas_credentials, uri, data)
                    has_changed = True
                #Delete associated Nodes
                i = 0
                uri = '/caas/2.1/'+orgId+'/networkDomainVip/deleteNode'
                while i < poolMembers['totalCount']:
                    if module.check_mode: has_changed=True
                    else: 
                        _data['id'] = poolMembers['poolMember'][i]['node']['id']
                        data = json.dumps(_data)
                        result = caasAPI(module,caas_credentials, uri, data)
                        has_changed = True
                    i += 1

#PRESENT
    if state == "present":
        if virtualListenerList['totalCount'] == 1: module.params['id'] = virtualListenerList['virtualListener'][0]['id']
        if virtualListenerList['totalCount'] < 1:
            uri = '/caas/2.1/'+orgId+'/networkDomainVip/createVirtualListener'
            _data = {}
            _data['name'] = module.params['name']
            _data['description'] = module.params['description']
            _data['networkDomainId'] = module.params['networkDomainId']
            _data['type'] = module.params['type']
            _data['protocol'] = module.params['protocol']
            _data['listenerIpAddress'] = module.params['listenerIpAddress']
            _data['port'] = module.params['port']
            _data['enabled'] = module.params['enabled']
            _data['connectionLimit'] = module.params['connectionLimit']
            _data['connectionRateLimit'] = module.params['connectionRateLimit']
            _data['sourcePortPreservation'] = module.params['sourcePortPreservation']
            _data['optimizationProfile'] = module.params['optimizationProfile']
            data = json.dumps(_data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True
                for info in result['info']:
                    if info['name'] == 'virtualListenerId': module.params['id'] = info['value']
        if module.params['pool']:
#TODO chack if poolid in vip
            if not 'name' in module.params['pool']: module.params['pool']['name']= module.params['name']+'.pool'
            f = { 'name' : module.params['pool']['name'], 'datacenterId' : module.params['datacenterId'], 'networkDomainId' : module.params['networkDomainId']}
            uri = '/caas/2.1/'+orgId+'/networkDomainVip/pool?'+urllib.urlencode(f)
            poolList = caasAPI(module,caas_credentials, uri, '')
            if poolList['totalCount'] == 1: module.params['pool']['id'] = poolList['pool'][0]['id']
            if poolList['totalCount'] < 1:
                uri = '/caas/2.1/'+orgId+'/networkDomainVip/createPool'
                _data = {}
                _data['networkDomainId'] = module.params['networkDomainId']
                _data['name'] = module.params['pool']['name']
                if 'description' in module.params['pool']: _data['description'] = module.params['pool']['description']
                else: _data['description'] = module.params['description']
                if 'loadBalanceMethod' in module.params['pool']: _data['loadBalanceMethod'] = module.params['pool']['loadBalanceMethod']
                else: _data['loadBalanceMethod'] = 'ROUND_ROBIN'
                #_data['healthMonitorId'] = module.params['pool']['healthMonitorId']
                if 'serviceDownAction' in module.params['pool']: _data['serviceDownAction'] = module.params['pool']['serviceDownAction']
                else: _data['serviceDownAction'] = 'RESELECT'
                if 'slowRampTime' in module.params['pool']: _data['slowRampTime'] = module.params['pool']['slowRampTime']
                else: _data['slowRampTime'] = 30
                data = json.dumps(_data)
                if module.check_mode: has_changed=True
                else: 
                    result = caasAPI(module,caas_credentials, uri, data)
                    has_changed = True
                    for info in result['info']:
                        if info['name'] == 'poolId': module.params['pool']['id'] = info['value']
                uri = '/caas/2.1/'+orgId+'/networkDomainVip/editVirtualListener'
                _data = {}
                _data['id'] = module.params['id']
                _data['poolId'] = module.params['pool']['id']
                data = json.dumps(_data)
                if module.check_mode: has_changed=True
                else: 
                    result = caasAPI(module,caas_credentials, uri, data)
                    has_changed = True
            for node in module.params['pool']['node']:
                logging.debug("--Node"+str(node))
                f = { 'name' : node['name'], 'datacenterId' : module.params['datacenterId'], 'networkDomainId' : module.params['networkDomainId']}
                uri = '/caas/2.1/'+orgId+'/networkDomainVip/node?'+urllib.urlencode(f)
                nodeList = caasAPI(module,caas_credentials, uri, '')
                if nodeList['totalCount'] < 1:
                    uri = '/caas/2.1/'+orgId+'/networkDomainVip/createNode'
                    _data = {}
                    _data['networkDomainId'] = module.params['networkDomainId']
                    _data['name'] = node['name']
                    _data['description'] = node['description']
                    _data['ipv4Address'] = node['ipv4Address']
                    #_data['ipv6Address'] = node['ipv6Address']
                    _data['status'] = node['status']
                    #_data['healthMonitorId'] = node['healthMonitorId']
                    _data['connectionLimit'] = node['connectionLimit']
                    _data['connectionRateLimit'] = node['connectionRateLimit']
                    data = json.dumps(_data)
                    if module.check_mode: has_changed=True
                    else: 
                        result = caasAPI(module,caas_credentials, uri, data)
                        has_changed = True
                        for info in result['info']:
                            if info['name'] == 'nodeId': node['id'] = info['value']
                    uri = '/caas/2.1/'+orgId+'/networkDomainVip/addPoolMember'
                    _data = {}
                    _data['poolId'] = module.params['pool']['id']
                    _data['nodeId'] = node['id']
                    _data['port'] = node['port']
                    _data['status'] = node['status']
                    data = json.dumps(_data)
                    if module.check_mode: has_changed=True
                    else: 
                        result = caasAPI(module,caas_credentials, uri, data)
                        has_changed = True

    f = { 'name' : module.params['name'], 'datacenterId' : module.params['datacenterId'], 'networkDomainId' : module.params['networkDomainId']}
    uri = '/caas/2.1/'+orgId+'/networkDomainVip/virtualListener?'+urllib.urlencode(f)
    virtualListenerList = caasAPI(module,caas_credentials, uri, '')

    module.exit_json(changed=has_changed, loadBalancers=virtualListenerList)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == '__main__':
    main()
