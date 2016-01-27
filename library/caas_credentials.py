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
  - "Check Dimension Data Managed Cloud Platform credentials"
  - "This step is optionnal"
module: caas_credentials
options: 
  apiurl: 
    description: 
      - "Africa (AF) : https://api-mea.dimensiondata.com"
      - "Asia Pacific (AP) : https://api-ap.dimensiondata.com"
      - "Australia (AU) : https://api-au.dimensiondata.com"
      - "Canada(CA) : https://api-canada.dimensiondata.com"
      - "Europe (EU) : https://api-eu.dimensiondata.com"
      - "North America (NA) : https://api-na.dimensiondata.com"
      - "South America (SA) : https://api-latam.dimensiondata.com"
    required: true
  datacenterId: 
    description: 
      - "You can use your own 'Private MCP', or any public MCP 2.0 below :"
      - "** Asia Pacific (AP) :"
      - "**** AP3 Singapore - Serangoon"
      - "**** AP4 Japan - Tokyo"
      - "** Australia (AU) :"
      - "**** AU9 Australia - Sydney"
      - "**** AU10  Australia - Melbourne"
      - "**** AU11 New Zealand - Hamilton"
      - "** Europe (EU) :"
      - "**** EU6 Germany - Frankfurt"
      - "**** EU7 Netherland - Amsterdam"
      - "**** EU8 UK - London"
      - "**** North America (NA) :"
      - "**** NA9 US - Ashburn"
      - "**** NA12 US - Santa Clara"
    required: true
  password: 
    description: 
      - "Your password"
    required: true
  username: 
    description: 
      - "Your username"
    required: true
short_description: "Check Dimension Data Managed Cloud Platform credentials"
version_added: "1.9"
'''

EXAMPLES = '''
# Check credentials with username/password provided inside playbook (not recommended)
tasks:
  - name: Check credentials (optionnal Step)
    caas_credentials:
        apiurl: https://api-eu.dimensiondata.com
        username: firstname.lastname
        password: MySecret_KeepItSecret
        datacenterId: EU6 
    register: cas_credentials
		
# Check credentials with username/password provided in an external file (recommended)
- name: Deploy Dimension Data infrastructure  
  hosts: localhost
  vars_files:
    - /root/caas_credentials.yml
  tasks:
    - name: Check credentials (optionnal Step)
      caas_credentials:
        username: "{{caas_credentials.username}}"
        password: "{{caas_credentials.password}}"
        apiurl: "{{caas_credentials.apiurl}}"
        datacenter: "{{caas_credentials.datacenter}}" 
      register: caas_credentials

# Content of the external file /root/caas_credentials.yml
caas_credentials:
    username: firstname.lastname
    password: MySecret_KeepItSecret
    apiurl: https://api-eu.dimensiondata.com
    datacenter: EU6 
'''

RETURN = '''
dest:
    description: destination file/path
    returned: success
    type: string
    sample: "/path/to/file.txt"
src:
    description: source file used for the copy on the target machine
    returned: changed
    type: string
    sample: "/home/httpd/.ansible/tmp/ansible-tmp-1423796390.97-147729857856000/source"
md5sum:
    description: md5 checksum of the file after running copy
    returned: when supported
    type: string
    sample: "2a5aeecc61dc98c4d780b14b330e3282"
...
'''

logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_credentials---"+str(datetime.datetime.now()))

def _getOrgId(caas_credentials):
    apiuri = '/oec/0.9/myaccount'
    request = urllib2.Request(caas_credentials['apiurl'] + apiuri)
    base64string = base64.encodestring('%s:%s' % (caas_credentials['username'], caas_credentials['password'])).replace('\n', '')
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

def main():
    module = AnsibleModule(
        argument_spec = dict(
            apiurl = dict(required=True),
            datacenter = dict(required=True),
            username = dict(required=True),
            password = dict(required=True,no_log=True),
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False
	
    # Check Authentication and get OrgId
    caas_credentials = {}
    caas_credentials['apiurl'] = module.params['apiurl']
    caas_credentials['datacenter'] = module.params['datacenter']
    caas_credentials['username'] = module.params['username']
    caas_credentials['password'] = module.params['password']
	
    result = _getOrgId(caas_credentials)
    if not result['status']:
        module.fail_json(msg=result['msg'])
    orgId = result['orgId']

	#Check dataCenterId
    #if not datacenterId
	
    module.exit_json(changed=has_changed, apiurl=caas_credentials['apiurl'], datacenter=caas_credentials['datacenter'], username=caas_credentials['username'], password=caas_credentials['password'], orgId=orgId)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
