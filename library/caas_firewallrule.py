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
module: caas_firewallrule
author: "Olivier GROSJEANNE, @job-so"
description: 
  - "Create, Configure, Remove Firewall Rules on Dimension Data Managed Cloud Platform"
short_description: "Create, Configure, Remove Firewall Rules on Dimension Data Managed Cloud Platform"
version_added: "1.9"
notes:
  - "This is a wrappper of Dimension Data CaaS API v2.1. Please refer to this documentation for more details and example : U(https://community.opsourcecloud.net/DocumentRevision.jsp?docId=7897c5018f9bca01cf2f4724de2bcfc5)"
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
      - "Name that has to be given to the rule"
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
  wait:
    description:
      - "Does the task must wait for the firewall rule creation ? or deploy it asynchronously ?"
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
  action:
    description:
      - "Accept or Drop ?"
    choices: ['ACCEPT_DECISIVELY','DROP']
    default: ACCEPT_DECISIVELY
  ipVersion:
    description:
      - "IPv4 or IPv6 ?"
    choices: ['IPV4','IPV6']
    default: IPV4
  protocol:
    description:
      - "IP or ICMP or TCP or UDP ?"
    choices: ['IP', 'ICMP', 'TCP', 'UDP']
    default: TCP
  enabled:
    description:
      - "enabled or disabled ?"
      - "This parameter is mutable (ie may be changed on an existiong rule)"
    choices: [True, False]
    default: True
  source.ip.address:
    description:
      - "The source.ip fields are used to limit the range of sources of network traffic allowed by the Firewall Rule. Three possible values :"
      - "1) ANY, in which case prefixSize is not used and source traffic is acceptable from any IP address."
      - "2) A valid IPv4 or IPv6 address depending on the ipVersion value selected, in which case traffic will be permitted from that specific IP address."
      - "3) A valid IPv4 or IPv6 network address depending on the ipVersion value selected, with a prefixSize."
    default: null
  source.ip.prefixSize:
    description:
      - "To define a range of addresses from which traffic will be permitted."
    default: null
  source.port.begin:
    description:
      - "source.port fields are only expected if TCP or UDP is selected as the protocol."
      - "To define a single port, supply the source.port.begin field by itself."
    default: null
  source.port.end:
    description:
      - "To define a range of ports, supply both the source.port.begin and source.port.end fields."
    default: null
  destination.ip.address:
    description:
      - "same as source.ip.address"
      - "Note that it is NOT possible to specify ANY for both the ource.ip.address and destination.ip.address if ipVersion is set to IPv6."
    default: null
  destination.ip.prefixSize:
    description:
      - "same as source.ip.prefixSize"
    default: null
  destination.port.begin:
    description:
      - "same as source.port.begin"
      - "Note that a port range can only be specified on either the source or destination - not both."
    default: null
  destination.port.end:
    description:
      - "same as source.port.end"
    default: null
  placement.position:
    description:
      - "FIRST, LAST, BEFORE or AFTER ?"
    choices: ['FIRST', 'LAST', 'BEFORE', 'AFTER']
    default: null
  placement.relativeToRule:
    description:
      - "If placement is set to BEFORE or AFTER, a relativeToRule field must be provided. The value of this should contain the name of an existing CLIENT_RULE on the Firewall Policy for the same Network Domain."
    default: null
'''

EXAMPLES = '''
# Creates a new firewall rule to allow traffic between 192.168.30.0/24 to 192.168.40.0/24 on tcp/3000 
        caas_firewallrule:
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "ansible.Caas_SandBox"
          name: "Web2App"
          source:
            ip:
              address: 192.168.30.0
              prefixSize: 24
          destination:
            ip:
              address: 192.168.40.0
              prefixSize: 24
            port:
              begin: 3000
          placement:
            position: "FIRST"

# Same rule with references from previous tasks.
        caas_firewallrule:
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "{{ caas_networkdomain.networkdomains.networkDomain[0].name }}"
          name: "Web2App"
          source:
            ip:
              address: "{{ caas_vlan_webservers.vlans.vlan[0].privateIpv4Range.address }}"
              prefixSize: "{{ caas_vlan_webservers.vlans.vlan[0].privateIpv4Range.prefixSize }}"
          destination:
            ip:
              address: "{{ caas_vlan_appservers.vlans.vlan[0].privateIpv4Range.address }}"
              prefixSize: "{{ caas_vlan_appservers.vlans.vlan[0].privateIpv4Range.prefixSize }}"
            port:
              begin: 3000
          placement:
            position: "FIRST"

# Disabling Default Rule that Drop Any external IPv6 connection
# Needed to allow ansible traffic to hosts after infrastructure deployment 
        caas_firewallrule:
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "{{ caas_networkdomain.networkdomains.networkDomain[0].name }}"
          name: "CCDEFAULT.DenyExternalInboundIPv6"
          enabled: False

# IPv6 rule from localhost (ansible machine) to a vlan deployed in a previous task.
# Needed to allow ansible traffic to hosts after infrastructure deployment
        caas_firewallrule:
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "{{ caas_networkdomain.networkdomains.networkDomain[0].name }}"
          name: "ssh_for_ansible_to_vlan_webservers"
          action: "ACCEPT_DECISIVELY"
          ipVersion: "IPV6"
          protocol: "TCP"
          source:
            ip:
              address: "{{ ansible_all_ipv6_addresses[0] }}"
          destination:
            ip:
              address: "{{ caas_vlan_webservers.vlans.vlan[0].ipv6Range.address }}"
              prefixSize: "{{ caas_vlan_webservers.vlans.vlan[0].ipv6Range.prefixSize }}"
            port:
              begin: 22
          placement:
            position: "LAST"

'''

RETURN = '''
        "firewallRules":
            type: Dictionary
            returned: success
            description: A list of firewallRule (should be one) matching the task parameters.
            sample: 
                "firewallRule":
                  - "action": "ACCEPT_DECISIVELY"
                    "datacenterId": "EU6"
                    "destination":
                        "ip":
                            "address": "192.168.40.0"
                            "prefixSize": 24
                        "port":
                            "begin": 3000
                    "enabled": true
                    "id": "8455537c-2cb8-482f-8212-f304e0acbaa7"
                    "ipVersion": "IPV4"
                    "name": "Web2App"
                    "networkDomainId": "94e50925-2d2f-4727-b137-6d70ce416829"
                    "protocol": "TCP"
                    "ruleType": "CLIENT_RULE"
                    "source":
                        "ip":
                            "address": "192.168.30.0"
                            "prefixSize": 24
                    "state": "NORMAL"
                "pageCount": 1
                "pageNumber": 1
                "pageSize": 50
                "totalCount": 1
...
'''

logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_firewallrule---"+str(datetime.datetime.now()))

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

def _listFirewallRule(module,caas_credentials,orgId,wait):
    f = { 'name' : module.params['name'], 'networkDomainId' : module.params['networkDomainId']}
    uri = '/caas/2.1/'+orgId+'/network/firewallRule?'+urllib.urlencode(f)
    b = True;
    while b:
        result = caasAPI(module,caas_credentials, uri, '')
        firewallRuleList = result
        b = False
        for (firewallRule) in firewallRuleList['firewallRule']:
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
            wait = dict(type='bool',default=True,choices=[True,False]),
            name = dict(required=True),
            action=dict(default='ACCEPT_DECISIVELY', choices = ['ACCEPT_DECISIVELY','DROP']),
            ipVersion=dict(default='IPV4', choices = ['IPV4','IPV6']),
            protocol=dict(default='TCP', choices = ['IP', 'ICMP', 'TCP','UDP']),
            networkDomainId = dict(default=None),
            networkDomainName = dict(default=None),
            source = dict(type='dict'),
            destination = dict(type='dict'),
            enabled = dict(type='bool',default=True, choices=[True, False]),
            placement = dict(type='dict'),
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

    orgId = _getOrgId(module,caas_credentials)

    if module.params['networkDomainId']==None:
        if module.params['networkDomainName']!=None:
            f = { 'name' : module.params['networkDomainName'], 'datacenterId' : module.params['datacenterId']}
            uri = '/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
            result = caasAPI(module,caas_credentials, uri, '')
            if result['totalCount']==1:
                module.params['networkDomainId'] = result['networkDomain'][0]['id']

    firewallList = _listFirewallRule(module,caas_credentials,orgId,True)
 
#ABSENT
    if state == 'absent':
        if firewallList['totalCount'] == 1:
            uri = '/caas/2.1/'+orgId+'/network/deleteFirewallRule'
            _data = {}
            _data['id'] = networkDomainList['networkDomain'][0]['id']
            data = json.dumps(_data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True

#PRESENT
    if state == "present":
        if firewallList['totalCount'] < 1:
            uri = '/caas/2.1/'+orgId+'/network/createFirewallRule'
            _data = {}
            _data['name'] = module.params['name']
            _data['action'] = module.params['action']
            _data['ipVersion'] = module.params['ipVersion']
            _data['protocol'] = module.params['protocol']
            _data['networkDomainId'] = module.params['networkDomainId']
            _data['source'] = module.params['source']
            _data['destination'] = module.params['destination']
            _data['enabled'] = module.params['enabled']
            _data['placement'] = module.params['placement']
            data = json.dumps(_data)
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True
        if firewallList['totalCount'] == 1:
            if firewallList['firewallRule'][0]['enabled'] != module.params['enabled']: 
                uri = '/caas/2.1/'+orgId+'/network/editFirewallRule'
                _data = {}
                _data['id'] = firewallList['firewallRule'][0]['id']
                _data['enabled'] = module.params['enabled']
                data = json.dumps(_data)
                if module.check_mode: has_changed=True
                else: 
                    result = caasAPI(module,caas_credentials, uri, data)
                    has_changed = True

    firewallRuleList = _listFirewallRule(module,caas_credentials,orgId,wait)
    module.exit_json(changed=has_changed, firewallRules=firewallRuleList)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == '__main__':
    main()
