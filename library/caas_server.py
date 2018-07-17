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
module: caas_server
author: "Olivier GROSJEANNE, @job-so"
short_description: "Create, Configure, Remove Servers on Dimension Data Managed Cloud Platform"
version_added: "1.9"
description: 
  - "Create, Configure, Remove Servers on Dimension Data Managed Cloud Platform"
notes:
  - "This is a wrappper of Dimension Data CaaS API v2.1. Please refer to this documentation for more details and examples : U(https://community.opsourcecloud.net/DocumentRevision.jsp?docId=7897c5018f9bca01cf2f4724de2bcfc5)"
requirements:
    - a caas_credentials variable, see caas_credentials module.  
    - a network domain already deployed, see caas_networkdomain module.
    - a vlan already deployed, see caas_vlan module.
options: 
  caas_credentials: 
    description: 
      - Complexe variable containing credentials. From an external file or from module caas_credentials (See related documentation)
    required: true
  name: 
    description: 
      - "Name that has to be given to the instance Minimum length 1 character Maximum length 75 characters."
    required: true
  count: 
    default: 1
    description: 
      - "Number of instances to deploy. This parameter is mutable, however decreasing as no effect."
  state:  
    choices: ['present','absent']
    default: present
    description: 
      - "Should the resource be present or absent."
      - "Take care : Absent will powerOff and delete all servers."
  start:  
    choices: [True,False]
    default: True
    description: 
      - "True indicates that the Server will be started following deployment."
  action: 
    description:
      - "Action to perform against all servers."
      - "** startServer : starts non-running Servers"            
      - "** shutdownServer : performs guest OS initiated shutdown of running Servers (preferable to powerOffServer)"
      - "** rebootServer : performs guest OS initiated restart of running Servers (preferable to resetServer)"
      - "** resetServer : performs hard reset of running Servers"
      - "** powerOffServer : performs hard power off of running Servers"
      - "** updateVmwareTools : triggers an update of the VMware Tools software running on the guest OS of the Servers"
      - "** upgradeVirtualHardware : triggers an update of the VMware Virtual Hardware. VMware recommend cloning the Server prior to performing the upgrade in case something goes wrong during the upgrade process"
    choices: ['startServer', 'shutdownServer', 'rebootServer', 'resetServer', 'powerOffServer', 'updateVmwareTools', 'upgradeVirtualHardware']
    default: Null
  wait:
    description:
      - "Does the task must wait for the server(s) creation ? or deploy it asynchronously ?"
    choices: [true,false]
    default: true
  description:
    description:
      - "Maximum length: 255 characters."
    default: "Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS"
  imageId:
    description:
      - "The id of the Server Image being used as the target for the new Server deployment"
      - "You can use either imageId or imageName, however one of them must be specified"
    default: Null
  imageName:
    description:
      - "The name of the Server Image being used as the target for the new Server deployment"
      - "You can use either imageId or imageName, however one of them must be specified"
    default: Null
  administratorPassword:
    description:
      - "The administrator password for Windows Servers,"
      - "The root password for Linux Servers."
    default: Null
  networkInfo:
    description:
      - "For an MCP 2.0 request, a networkInfo element is required. networkInfo identifies the Network Domain to which the Server will be deployed."
      - "It contains a primaryNic element defining the required NIC for the Server and optional additionalNic elements defining any additional VLAN connections for the Server."
      - "Each NIC must contain either a VLAN ID (vlanId) OR a Private IPv4 address (privateIpv4) from the target VLAN which the NIC will associate the Server with."
    default: Null
  networkInfo.networkDomainId:
    description:
      - "The id of a Network Domain belonging within the same MCP 2.0 data center."
      - "You can use either networkInfo.networkDomainId or networkDomainName, however one of them must be specified"
    default: null
  networkInfo.networkDomainName:
    description:
      - "The name of a Network Domain belonging within the same MCP 2.0 data center."
      - "You can use either networkInfo.networkDomainId or networkDomainName, however one of them must be specified"
    default: null
  networkInfo.primaryNic.privateIpv4:
    description:
      - "RFC1918 Dot-decimal representation of an IPv4 address."
      - "For example: “192.168.30.42”. Must be unique within the Network Domain."
      - "You can use either networkInfo.primaryNic.privateIpv4 or networkInfo.primaryNic.vlanId or networkInfo.primaryNic.vlanName, however one of them must be specified"
    default: null
  networkInfo.primaryNic.vlanId:
    description:
      - "The id of a Vlan belonging within the same Network Domain."
      - "You can use either networkInfo.primaryNic.privateIpv4 or networkInfo.primaryNic.vlanId or networkInfo.primaryNic.vlanName, however one of them must be specified"
    default: null
  networkInfo.primaryNic.vlanName:
    description:
      - "The name of a Vlan belonging within the same Network Domain."
      - "You can use either networkInfo.primaryNic.privateIpv4 or networkInfo.primaryNic.vlanId or networkInfo.primaryNic.vlanName, however one of them must be specified"
    default: null
  cpu:
    description:
      - "Can be used to override CPU values inherited from the source Server Image (imageName or imageId)"
    default: Null
  cpu.speed:
    description:
      - "Determines the CPU Speed to be used across all of the CPUs on the Server"
    default: Null
  cpu.count:
    description:
      - "Overrides the number of CPUs specified on the source Server Image."
      - "Note the relationship between this value and the coresPerSocket value."
    default: Null
  cpu.coresPerSocket:
    description:
      - "Must must be an integer factor of CPU count."
      - "The default and recommended value for cores per socket is 1."
    default: Null
  memoryGb:
    description:
      - "Can be used to override the memory value inherited from the source Server Image (imageName or imageId)"
    default: Null
  disk:
    description:
      - "Optional disk elements can be used to define the disk speed that each disk on the Server – inherited from the source Server Image - will be deployed to"
      - "disk.scsiId and disk.speed"
    default: Null
  microsoftTimeZone:
    description:
      - "For use with Microsoft Windows source Server Images (imageId) only."
      - "For the exact value to use please refer to the table of time zone indexes in Microsoft Technet"
    default: Null
'''


EXAMPLES = '''
# Create a new server named "MyWebServer" of CentOS 7 with default CPU/RAM/HD, 
#   with a specific IP (vlan is determined based on this IPv4), in Network Domain : "ansible.Caas_SandBox"
      - name: Deploy WebServers DMZ
        caas_server:
          caas_credentials: "{{ caas_credentials }}"
          name: "MyWebServer"
          imageName: CentOS 7 64-bit 2 CPU
          administratorPassword: "{{ root_password }}"
          networkInfo:
              networkDomainName: ansible.Caas_SandBox
              primaryNic: 
                  privateIpv4: 192.168.30.42
        register: caas_mywebserver

# shutdown this server
      - name: Deploy WebServers DMZ
        caas_server:
          caas_credentials: "{{ caas_credentials }}"
          name: "MyWebServer"
          action: shutdownServer
          networkInfo:
              networkDomainName: ansible.Caas_SandBox
              primaryNic: 
                  privateIpv4: 192.168.30.42

# teardown this server (no need to ShutDown/PowerOff)
      - name: Deploy WebServers DMZ
        caas_server:
          caas_credentials: "{{ caas_credentials }}"
          name: "MyWebServer"
          state: absent
          networkInfo:
              networkDomainName: ansible.Caas_SandBox
              primaryNic: 
                  privateIpv4: 192.168.30.42

# Create 2 servers named "WebServer" of CentOS 7 with default CPU/RAM/HD, 
#   automatic IPv4 assignement, in a vlan and a Network Domain referenced from a previous task.
      - name: Deploy WebServers
        caas_server:
          caas_credentials: "{{ caas_credentials }}"
          name: "WebServer"
          count: 2
          imageName: CentOS 7 64-bit 2 CPU
          administratorPassword: "{{ root_password }}"
          networkInfo:
              networkDomainName: "{{ caas_networkdomain.networkdomains.networkDomain[0].name }}"
              primaryNic: 
                  vlanName: "{{caas_vlan_webservers.vlans.vlan[0].name}}"
        register: caas_webservers
# and add this 2 new servers to Ansible dynamic inventoy (Group : WebServers)
      - name: Add new instances to group WebServers
        add_host: name="{{ item.id }}" ansible_ssh_host="{{ item.networkInfo.primaryNic.ipv6 }}" ansible_ssh_pass="{{ root_password }}" groupname=WebServers
        when: item.started
        with_items: "{{caas_webservers.servers.server}}"
#you can now apply roles ands tasks, as usual
  - name: Configure Web Servers
    hosts: WebServers
    vars_files:
      - /root/main.yml
    roles:
      - { role: my.apache }
      - { role: my.php }
'''

RETURN = '''
        "servers": 
            type: Dictionary
            returned: success
            description: A list of Servers (one, or more) matching the task parameters.
            sample: 
                "pageCount": 1
                "pageNumber": 1
                "pageSize": 250
                "server":
                  - "cpu":
                        "coresPerSocket": 1
                        "count": 2
                        "speed": "STANDARD"
                    "createTime": "2016-01-28T15:47:34.000Z"
                    "datacenterId": "EU6"
                    "deployed": true
                    "description": "Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS"
                    "disk":
                      - "id": "3ef2ac30-0b64-4dd1-bd24-a01780ea6b7e"
                        "scsiId": 0
                        "sizeGb": 10
                        "speed": "STANDARD"
                        "state": "NORMAL"
                    "id": "029383e1-6912-45fb-a604-5c7d2e9e0998"
                    "memoryGb": 4
                    "name": "MyWebServer"
                    "networkInfo":
                        "additionalNic": []
                        "networkDomainId": "94e50925-2d2f-4727-b137-6d70ce416829"
                        "primaryNic":
                            "id": "1ab80e75-ca8b-490f-8105-f17a0e3c78af"
                            "ipv6": "2a00:47c0:111:1168:82b:fb61:c846:7758"
                            "privateIpv4": "192.168.30.42"
                            "state": "NORMAL"
                            "vlanId": "3a454c87-c8f6-4517-8531-b55f9440449c"
                            "vlanName": "ansible.CaaS_Sandbox_vlan_webservers"
                    "operatingSystem":
                        "displayName": "CENTOS7/64"
                        "family": "UNIX"
                        "id": "CENTOS764"
                    "softwareLabel": []
                    "sourceImageId": "d265499b-842d-46b1-a5aa-719971510e06"
                    "started": true
                    "state": "NORMAL"
                    "virtualHardware":
                        "upToDate": false
                        "version": "vmx-08"
                    "vmwareTools":
                        "apiVersion": 9354
                        "runningStatus": "RUNNING"
                        "versionStatus": "CURRENT"
                "totalCount": 1
...
'''

logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_server---"+str(datetime.datetime.now()))

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

def _listServer(module,caas_credentials,orgId,wait):
    # List Servers with this Name, in this networkDomain, in this vlanId
    if 'vlanId' in module.params['networkInfo']['primaryNic']:
        f = { 'networkDomainId' : module.params['networkInfo']['networkDomainId'], 'vlanId' : module.params['networkInfo']['primaryNic']['vlanId'], 'name' : module.params['name']}
    else: 
        if 'privateIpv4' in module.params['networkInfo']['primaryNic']:
           f = { 'networkDomainId' : module.params['networkInfo']['networkDomainId'], 'privateIpv4' : module.params['networkInfo']['primaryNic']['privateIpv4'], 'name' : module.params['name']}
        else:
            return None;
    uri = '/caas/2.3/'+orgId+'/server/server?'+urllib.urlencode(f)
    b = True
    while b:
        result = caasAPI(module,caas_credentials, uri, '')
        serverList = result
        b = False
        for (server) in serverList['server']:
            logging.debug(server['id']+' '+server['name']+' '+server['state'])
            if (server['state'] != "NORMAL") and wait == True:
                b = True
        if b:
            time.sleep(5)
    return serverList

def _executeAction(module,caas_credentials,orgId,serverList,action):
    logging.debug("---_executeAction "+action)
    has_changed = False
    _data = {}
    uri = '/caas/2.3/'+orgId+'/server/'+action
    if 'server' in serverList:
      for (server) in serverList['server']:
          logging.debug(server['id'])
          _data['id'] = server['id']
          data = json.dumps(_data)
          if not server['started'] and (action == "startServer" or action == "updateVmwareTools" or action == "deleteServer"):
              if module.check_mode: has_changed=True
              else: 
                  result = caasAPI(module,caas_credentials, uri, data)
                  has_changed = True
          if server['started'] and (action == "shutdownServer" or action == "powerOffServer" or action == "resetServer" or action == "rebootServer" or action == "upgradeVirtualHardware"):
              if module.check_mode: has_changed=True
              else: 
                  result = caasAPI(module,caas_credentials, uri, data)
                  has_changed = True
    return has_changed
    
def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec = dict(
            caas_credentials = dict(type='dict',required=True,no_log=True),
            name = dict(required=True),
            count = dict(type='int', default='1'),
            state = dict(default='present', choices=['present', 'absent']),
            start = dict(type='bool',default=True, choices=[True,False]),
            action = dict(default=None, choices=['startServer', 'shutdownServer', 'rebootServer', 'resetServer', 'powerOffServer', 'updateVmwareTools', 'upgradeVirtualHardware']),
            wait = dict(default=True),
            description = dict(default='Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS'),
            imageId = dict(default=None),
            imageName = dict(default=None),
            administratorPassword = dict(default='',no_log=True),
            networkInfo = dict(type='dict'),
            cpu = dict(type='dict'),
            memoryGb = dict(default=None),
            disk = dict(type='dict'),
            microsoftTimeZone = dict(default=None),
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False
    
    # Check Authentication and get OrgId
    caas_credentials = module.params['caas_credentials']
    module.params['datacenterId'] = module.params['caas_credentials']['datacenter']
    module.params.pop('caas_credentials', None)

    orgId = _getOrgId(module, caas_credentials)

    # resolve imageId, networkId, vlanId
    if module.params['imageId']== None:
        if module.params['imageName']!=None:
            f = { 'datacenterId' : module.params['datacenterId'], 'name' : module.params['imageName'] }
            uri = '/caas/2.3/'+orgId+'/image/osImage?'+urllib.urlencode(f)
            result = caasAPI(module,caas_credentials, uri, '')
            if result['totalCount']==1:
                module.params['imageId'] = result['osImage'][0]['id']
    if not 'networkDomainId' in module.params['networkInfo']:
        if 'networkDomainName' in module.params['networkInfo']:
            f = { 'name' : module.params['networkInfo']['networkDomainName'], 'datacenterId' : module.params['datacenterId']}
            uri = '/caas/2.3/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
            result = caasAPI(module,caas_credentials, uri, '')
            if result['totalCount']==1:
                module.params['networkInfo']['networkDomainId'] = result['networkDomain'][0]['id']
    if 'primaryNic' in module.params['networkInfo']:
        if not 'vlanId' in module.params['networkInfo']['primaryNic']:
            if 'vlanName' in module.params['networkInfo']['primaryNic']:
                f = { 'name' : module.params['networkInfo']['primaryNic']['vlanName'], 'datacenterId' : module.params['datacenterId']}
                uri = '/caas/2.3/'+orgId+'/network/vlan?'+urllib.urlencode(f)
                result = caasAPI(module, caas_credentials, uri, '')
                if result['totalCount']==1:
                    module.params['networkInfo']['primaryNic']['vlanId'] = result['vlan'][0]['id']
    
    serverList = _listServer(module,caas_credentials,orgId,True)
    
#ABSENT
    if (module.params['state']=='absent') and (serverList != None):
        if serverList['totalCount']>=1:
            has_changed = _executeAction(module, caas_credentials, orgId, serverList, 'powerOffServer') or has_changed
            serverList = _listServer(module,caas_credentials,orgId,True)
            has_changed = _executeAction(module, caas_credentials, orgId, serverList, 'deleteServer') or has_changed

#PRESENT
    if module.params['state'] == "present":
        i = serverList['totalCount']
        uri = '/caas/2.3/'+orgId+'/server/deployServer'
        data = json.dumps(module.params)
        while i < module.params['count']:
            if module.check_mode: has_changed=True
            else: 
                result = caasAPI(module,caas_credentials, uri, data)
                has_changed = True
            i += 1            

        # Execute Action on Servers
        if module.params['action']!=None:
            has_changed = _executeAction(module, caas_credentials,orgId,serverList,module.params['action']) or has_changed

    module.exit_json(changed=has_changed, servers=_listServer(module,caas_credentials,orgId,module.params['wait']))

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == '__main__':
    main()
