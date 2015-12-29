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
short_description: Create or Remove Servers on Dimension Data Managed Cloud Platform
version_added: "0.4"
author: "Olivier GROSJEANNE (@grosjeanne)"
description:
   - Create or Remove Servers on Dimension Data Managed Cloud Platform
options:
   name:
     description:
        - Name that has to be given to the instance
     required: true
   state:
     description:
       - Should the resource be present or absent.
     choices: [present, absent]
     default: present
'''

EXAMPLES = '''
# Creates a new instance of CentOS on and attaches to a network and passes metadata to
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
            result['msg'] = json.loads(response.read())
            result['status'] = True
        except urllib2.HTTPError, e:
            result['msg'] = json.loads(e.read())
            if result['msg']['responseCode'] == "RESOURCE_BUSY":
                logging.debug("RESOURCE_BUSY "+str(retryCount)+"/30")
                time.sleep(10)
                retryCount += 1
            else:
                retryCount = 9999
        except urllib2.URLError as e:
            result['msg'] = e.reason
            retryCount = 9999
    return result

def main():
    module = AnsibleModule(
        argument_spec = dict(
            caas_apiurl = dict(required=True),
            caas_datacenter = dict(required=True),
            caas_username = dict(required=True),
            caas_password = dict(required=True,no_log=True),
			name = dict(required=True),
			count = dict(type='int', default='1'),
            state = dict(default='present', choices=['present', 'absent']),
            action = dict(default='startServer', choices=['startServer', 'shutdownServer', 'rebootServer', 'resetServer', 'powerOffServer', 'updateVmwareTools', 'upgradeVirtualHardware']),
            wait = dict(default=True),
            description = dict(default='Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS'),
            imageId = dict(default=''),
            imageName = dict(default=''),
            administratorPassword = dict(default='',no_log=True),
            networkInfo = dict(),
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

	#Check dataCenterId
    #if not datacenterId
	
	# resolve imageId, networkId, vlanId
    if module.params['imageId']=='':
        if module.params['imageName']!='':
            f = { 'datacenterId' : module.params['caas_datacenter'], 'name' : module.params['imageName'] }
            uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/image/osImage?'+urllib.urlencode(f)
            result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
            if result['status']:
                if result['msg']['totalCount']==1:
                    module.params['imageId'] = result['msg']['osImage'][0]['id']
    if not 'networkDomainId' in module.params['networkInfo']:
        if 'networkDomainName' in module.params['networkInfo']:
            f = { 'name' : module.params['networkInfo']['networkDomainName']}
            uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
            result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
            if result['status']:
                if result['msg']['totalCount']==1:
                    module.params['networkInfo']['networkDomainId'] = result['msg']['networkDomain'][0]['id']
    if 'primaryNic' in module.params['networkInfo']:
        if not 'vlanId' in module.params['networkInfo']['primaryNic']:
            if 'vlanName' in module.params['networkInfo']['primaryNic']:
                f = { 'name' : module.params['networkInfo']['primaryNic']['vlanName']}
                uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/network/vlan?'+urllib.urlencode(f)
                result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
                if result['status']:
                    if result['msg']['totalCount']==1:
                        module.params['networkInfo']['primaryNic']['vlanId'] = result['msg']['vlan'][0]['id']
	
	# List Servers with this Name, in this networkDomain, in this vlanId
    f = { 'networkDomainId' : module.params['networkInfo']['networkDomainId'], 'vlanId' : module.params['networkInfo']['primaryNic']['vlanId'], 'name' : module.params['name']}
    uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/server?'+urllib.urlencode(f)
    b = True;
    while module.params['wait'] and b:
        result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
        serverList = result['msg']
        b = False
        for (server) in serverList['server']:
            logging.debug(server['id']+' '+server['name']+' '+server['state'])
            if server['state'] != "NORMAL":
		        b = True
        if b:
            time.sleep(5)
	
	# Execute Action on Servers
    _data = {}
    uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/'+module.params['action']
    for (server) in serverList['server']:
        logging.debug(server['id'])
        _data['id'] = server['id']
        data = json.dumps(_data)
        if not server['started'] and (module.params['action'] == "startServer" or module.params['action'] == "updateVmwareTools"):
            result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, data)
            if not result['status']:
                module.fail_json(msg=result['msg'])
            else:
                has_changed = True	
        if server['started'] and (module.params['action'] == "shutdownServer" or module.params['action'] == "powerOffServer" or module.params['action'] == "resetServer" or module.params['action'] == "rebootServer" or module.params['action'] == "upgradeVirtualHardware"):
            result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, data)
            if not result['status']:
                module.fail_json(msg=result['msg'])
            else:
                has_changed = True	

	# Deploy New Servers if needed
    if module.params['state'] == "present":
        i = serverList['totalCount']
        uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/deployServer'
        module.params['start'] = (module.params['action'] == 'startServer')
        data = json.dumps(module.params)
        while i < module.params['count']:
            result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, data)
            if not result['status']:
                module.fail_json(msg=result['msg'])
            else:
                has_changed = True
	    i += 1			
		
    # List Servers with this Name
    f = { 'networkDomainId' : module.params['networkInfo']['networkDomainId'], 'vlanId' : module.params['networkInfo']['primaryNic']['vlanId'], 'name' : module.params['name']}
    uri = module.params['caas_apiurl']+'/caas/2.1/'+orgId+'/server/server?'+urllib.urlencode(f)
    b = True;
    while module.params['wait'] and b:
        result = caasAPI(module.params['caas_username'],module.params['caas_password'], uri, '')
        serverList = result['msg']
        b = False
        for (server) in serverList['server']:
            logging.debug(server['id']+' '+server['name']+' '+server['state'])
            if server['state'] != "NORMAL":
		        b = True
        if b:
            time.sleep(5)

    module.exit_json(changed=has_changed, servers=result['msg'])

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
