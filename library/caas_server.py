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
module: caas_server
short_description: Create/Delete Servers on Dimension Data Managed Cloud Platforms
version_added: "0.4"
author: "Olivier GROSJEANNE (@grosjeanne)"
description:
   - Create or Remove server instances from OpenStack.
options:
   name:
     description:
        - Name that has to be given to the instance
     required: true
   image:
     description:
        - The name or id of the base image to boot.
     required: true
   image_exclude:
     description:
        - Text to use to filter image names, for the case, such as HP, where
          there are multiple image names matching the common identifying
          portions. image_exclude is a negative match filter - it is text that
          may not exist in the image name. Defaults to "(deprecated)"
   flavor:
     description:
        - The name or id of the flavor in which the new instance has to be
          created. Mutually exclusive with flavor_ram
     required: false
     default: 1
   flavor_ram:
     description:
        - The minimum amount of ram in MB that the flavor in which the new
          instance has to be created must have. Mutually exclusive with flavor.
     required: false
     default: 1
   flavor_include:
     description:
        - Text to use to filter flavor names, for the case, such as Rackspace,
          where there are multiple flavors that have the same ram count.
          flavor_include is a positive match filter - it must exist in the
          flavor name.
   key_name:
     description:
        - The key pair name to be used when creating a instance
     required: false
     default: None
   security_groups:
     description:
        - Names of the security groups to which the instance should be
          added. This may be a YAML list or a comma separated string.
     required: false
     default: None
   network:
     description:
        - Name or ID of a network to attach this instance to. A simpler
          version of the nics parameter, only one of network or nics should
          be supplied.
     required: false
     default: None
   nics:
     description:
        - A list of networks to which the instance's interface should
          be attached. Networks may be referenced by net-id/net-name/port-id
          or port-name.
        - 'Also this accepts a string containing a list of (net/port)-(id/name)
          Eg: nics: "net-id=uuid-1,port-name=myport"
          Only one of network or nics should be supplied.'
     required: false
     default: None
   auto_ip:
     description:
        - Ensure instance has public ip however the cloud wants to do that
     required: false
     default: 'yes'
     aliases: ['auto_floating_ip', 'public_ip']
   floating_ips:
     description:
        - list of valid floating IPs that pre-exist to assign to this node
     required: false
     default: None
   floating_ip_pools:
     description:
        - list of floating IP pools from which to choose a floating IP
     required: false
     default: None
   meta:
     description:
        - 'A list of key value pairs that should be provided as a metadata to
          the new instance or a string containing a list of key-value pairs.
          Eg:  meta: "key1=value1,key2=value2"'
     required: false
     default: None
   wait:
     description:
        - If the module should wait for the instance to be created.
     required: false
     default: 'yes'
   timeout:
     description:
        - The amount of time the module should wait for the instance to get
          into active state.
     required: false
     default: 180
   config_drive:
     description:
        - Whether to boot the server with config drive enabled
     required: false
     default: 'no'
   userdata:
     description:
        - Opaque blob of data which is made available to the instance
     required: false
     default: None
   boot_from_volume:
     description:
        - Should the instance boot from a persistent volume created based on
          the image given. Mututally exclusive with boot_volume.
     required: false
     default: false
   volume_size:
     description:
        - The size of the volume to create in GB if booting from volume based
          on an image.
   boot_volume:
     description:
        - Volume name or id to use as the volume to boot from. Implies
          boot_from_volume. Mutually exclusive with image and boot_from_volume.
     required: false
     default: None
     aliases: ['root_volume']
   terminate_volume:
     description:
        - If true, delete volume when deleting instance (if booted from volume)
     default: false
   volumes:
     description:
       - A list of preexisting volumes names or ids to attach to the instance
     required: false
     default: []
   state:
     description:
       - Should the resource be present or absent.
     choices: [present, absent]
     default: present
requirements:
    - "python >= 2.6"
    - "shade"
'''

EXAMPLES = '''
# Creates a new instance and attaches to a network and passes metadata to
# the instance
- os_server:
       state: present
       auth:
         auth_url: https://region-b.geo-1.identity.hpcloudsvc.com:35357/v2.0/
         username: admin
         password: admin
         project_name: admin
       name: vm1
       image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
       key_name: ansible_key
       timeout: 200
       flavor: 4
       nics:
         - net-id: 34605f38-e52a-25d2-b6ec-754a13ffb723
         - net-name: another_network
       meta:
         hostname: test1
         group: uge_master
'''

logging.basicConfig(filename='caas-server.log',level=logging.DEBUG)
logging.debug(str(datetime.datetime.now()))

def getOrgId(username, password, apiurl):
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
            result['msg'] = response.read()
            result['status'] = True
        except urllib2.HTTPError, e:
            result['msg'] = e.read()
            if (json.loads(result['msg'])['responseCode'] == "RESOURCE_BUSY"):
                logging.debug("RESOURCE_BUSY "+str(retryCount)+"/30")
                time.sleep(10)
                retryCount += 1
            else:
                retryCount = 9999
        except urllib2.URLError as e:
            result['msg'] = result['msg'] + e.reason
            retryCount = 9999
    return result

def main():
    module = AnsibleModule(
        argument_spec = dict(
            caas_apiurl = dict(required=True),
            caas_username = dict(required=True),
            caas_password = dict(required=True),
			name = dict(required=True),
			count = dict(type='int', default='1'),
            state = dict(default='present', choices=['present', 'absent']),
            action = dict(default='deployServer', choices=['deployServer', 'deleteServer', 'startServer', 'stopServer', 'shutdownServer', 'rebootServer', 'resetServer', 'powerOffServer', 'updateVmwareTools', 'upgradeVirtualHardware']),
			data = dict(required=True),
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False
	
    # Check Authentication and get OrgId
    result = getOrgId(module.params['caas_username'],module.params['caas_password'],module.params['caas_apiurl'])
    if not result['status']:
        module.fail_json(msg=result['msg'])
    orgId = result['orgId']

	# resolve networkId, vlanId
    module.params['data']['name'] = module.params['name']
    if 'networkInfo' in module.params['data']:
        if not 'networkDomainId' in module.params['data']['networkInfo']:
            if 'networkDomainName' in module.params['data']['networkInfo']:
                f = { 'name' : module.params['data']['networkInfo']['networkDomainName']}
                uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
                result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
                if result['status']:
                    module.params['data']['networkInfo']['networkDomainId'] = json.loads(result['msg'])['networkDomain'][0]['id']
        if 'primaryNic' in module.params['data']['networkInfo']:
            if not 'vlanId' in module.params['data']['networkInfo']['primaryNic']:
                if 'vlanName' in module.params['data']['networkInfo']['primaryNic']:
                    f = { 'name' : module.params['data']['networkInfo']['primaryNic']['vlanName']}
                    uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/network/vlan?'+urllib.urlencode(f)
                    result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
                    if result['status']:
                        module.params['data']['networkInfo']['primaryNic']['vlanId'] = json.loads(result['msg'])['vlan'][0]['id']
	
	# List Servers with this Name, in this networkDomain, in this vlanId
    f = { 'networkDomainId' : module.params['data']['networkInfo']['networkDomainId'], 'vlanId' : module.params['data']['networkInfo']['primaryNic']['vlanId'], 'name' : module.params['name']}
    uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/server?'+urllib.urlencode(f)
    result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
    serverList = json.loads(result['msg'])
	
	# Execute Action on Servers
    if module.params['action'] != "deployServer":
        _data = {}
        uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/'+module.params['action']
        for (server) in serverList['server']:
            logging.debug(server['id'])
            _data['id'] = server['id']
            data = json.dumps(_data)
            result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, data)
            if not result['status']:
                module.fail_json(msg=result['msg'])
            else:
			    has_changed = True	

	# Deploy New Servers if needed
    if module.params['action'] == "deployServer":
        i = serverList['totalCount']
        uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/'+module.params['action']
        data = json.dumps(module.params['data'])
        while i < module.params['count']:
            result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, data)
            if not result['status']:
                module.fail_json(msg=result['msg'])
            else:
                has_changed = True
	    i += 1			
		
    # List Servers with this Name
    f = { 'networkDomainId' : module.params['data']['networkInfo']['networkDomainId'], 'vlanId' : module.params['data']['networkInfo']['primaryNic']['vlanId'], 'name' : module.params['name']}
    uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/server?'+urllib.urlencode(f)
    result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
    serverList = json.loads(result['msg'])

    module.exit_json(changed=has_changed, serverList=serverList)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
