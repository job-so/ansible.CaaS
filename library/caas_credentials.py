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
      - "** Africa (AF) :"
      - "**** AF3 South Africa - Johannesburg"
      - "** Asia Pacific (AP) :"
      - "**** AP3 Singapore - Serangoon"
      - "**** AP4 Japan - Tokyo"
      - "**** AP5 China - Hong Kong"
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
    vars:
      root_password: P$$ssWwrrdGoDd!
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
datacenter: 
    sample: "EU6"
orgId:
    sample: "4255d938-0bfc-4553-9c68-b61fbd1f4c42"
password:
    sample: "MySecret_KeepItSecret"
username:
    sample: "firstname.lastname"
'''

logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_credentials---"+str(datetime.datetime.now()))

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

def main():
    module = AnsibleModule(
        supports_check_mode=True,
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
    
    orgId = _getOrgId(module,caas_credentials)

    module.exit_json(changed=has_changed, apiurl=caas_credentials['apiurl'], datacenter=caas_credentials['datacenter'], username=caas_credentials['username'], password=caas_credentials['password'], orgId=orgId)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == '__main__':
    main()
