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
module: caas_publicip
author: "Olivier GROSJEANNE, @job-so"
description: 
  - "Get or Release Public IP addresses on Dimension Data Managed Cloud Platform"
short_description: "Get or Release Public IP addresses on Dimension Data Managed Cloud Platform"
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
  minFreePublicIpv4Address:
    description:
      - "The number of Public (ie internet) ipv4 you would like to have available to this networkDomain."
      - "If this parameter is higher than current ipv4 available, the module will reserve new ip."
      - "If this parameter is lower than current ipv4 available, the module will try to release existing (and not used) ip blocks."
      - "Setting this parameter to 0 will release all ip blocks if there is no nat or no load balancer setup in this networkdomain."
    default: 1
'''

EXAMPLES = '''
# Ensure that there is at least 1 public ipv4 available
      - name: Get Public IPv4
        caas_publicip:
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "{{ caas_networkdomain.networkdomains.networkDomain[0].name }}"
# Reserve at least 4 public ipv4
      - name: Get Public IPv4
        caas_publicip:
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "{{ caas_networkdomain.networkdomains.networkDomain[0].name }}"
          minFreePublicIpv4Address: 4
# Release all unused public ipv4 blocks
      - name: Get Public IPv4
        caas_publicip:
          caas_credentials: "{{ caas_credentials }}"
          networkDomainName: "{{ caas_networkdomain.networkdomains.networkDomain[0].name }}"
          minFreePublicIpv4Address: 0
'''

RETURN = '''
        "freePublicIpv4Address":
            type: integer
            returned: success
            description: The number of available public ip in the networkdomain
            sample: 1
        "publicIpBlocks":
            type: Dictionary
            returned: success
            description: A list of public IP blocks in the networkdomain.
            sample: 
                "publicIpBlock":
                  - "baseIp": "168.128.12.234"
                    "createTime": "2016-02-04T06:10:03.000Z"
                    "datacenterId": "EU6"
                    "id": "813e916e-18e1-11e5-8d4f-180373fb68df"
                    "networkDomainId": "cdb307d2-4438-4adf-8918-2ebc25ca27d2"
                    "size": 2
                    "state": "NORMAL"
                "pageCount": 1
                "pageNumber": 1
                "pageSize": 250
                "totalCount": 1
                "totalPublicIp": 2
        "reservedPublicIpv4Address":
            type: Dictionary
            returned: success
            description: A list of reserved (ie used) public ip in the networkdomain.
            sample: 
                "ip":
                  - "datacenterId": "EU6"
                    "ipBlockId": "813e916e-18e1-11e5-8d4f-180373fb68df"
                    "networkDomainId": "cdb307d2-4438-4adf-8918-2ebc25ca27d2"
                    "value": "168.128.12.234"
                "pageCount": 1
                "pageNumber": 1
                "pageSize": 250
                "totalCount": 1
...
'''

logging.basicConfig(filename='caas.log',level=logging.DEBUG)
logging.debug("--------------------------------caas_publicip---"+str(datetime.datetime.now()))

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

def caasAPI(caas_credentials, uri, data):
    logging.debug(uri)
    if data == '':
        request = urllib2.Request(caas_credentials['apiurl'] + uri)
    else:
        request    = urllib2.Request(caas_credentials['apiurl'] + uri, data)
    base64string = base64.encodestring('%s:%s' % (caas_credentials['username'], caas_credentials['password'])).replace('\n', '')
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

def _listPublicIpBlock(module,caas_credentials,orgId):
    f = { 'networkDomainId' : module.params['networkDomainId']}
    uri = '/caas/2.1/'+orgId+'/network/publicIpBlock?'+urllib.urlencode(f)
    result = caasAPI(caas_credentials, uri, '')
    if result['status']:
        publicIpList = result['msg']
        i = 0
        totalPublicIp = 0
        while i < publicIpList['totalCount']:
            totalPublicIp += publicIpList['publicIpBlock'][i]['size']
            i += 1
        publicIpList['totalPublicIp'] = totalPublicIp
    else:
        module.fail_json(msg=result['msg'])
    return publicIpList

def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec = dict(
            caas_credentials = dict(required=True,no_log=True),
            networkDomainId = dict(default=None),
            networkDomainName = dict(default=None),
            minFreePublicIpv4Address = dict(required=False,default=1),
        )
    )
    if not IMPORT_STATUS:
        module.fail_json(msg='missing dependencies for this module')
    has_changed = False
    
    # Check Authentication and get OrgId
    caas_credentials = module.params['caas_credentials']
    module.params['datacenterId'] = module.params['caas_credentials']['datacenter']
    module.params.pop('caas_credentials', None)

    result = _getOrgId(caas_credentials)
    if not result['status']:
        module.fail_json(msg=result['msg'])
    orgId = result['orgId']

    if module.params['networkDomainId']==None:
        if module.params['networkDomainName']!=None:
            f = { 'name' : module.params['networkDomainName'], 'datacenterId' : module.params['datacenterId']}
            uri = '/caas/2.1/'+orgId+'/network/networkDomain?'+urllib.urlencode(f)
            result = caasAPI(caas_credentials, uri, '')
            if result['status']:
                if result['msg']['totalCount']==1:
                    module.params['networkDomainId'] = result['msg']['networkDomain'][0]['id']

    publicIpList = _listPublicIpBlock(module,caas_credentials,orgId)

    f = { 'networkDomainId' : module.params['networkDomainId']}
    uri = '/caas/2.1/'+orgId+'/network/reservedPublicIpv4Address?'+urllib.urlencode(f)
    result = caasAPI(caas_credentials, uri, '')
    if result['status']:
        reservedPublicIpv4Address = result['msg']
        logging.debug("   reservedPublicIpv4Address:"+str(reservedPublicIpv4Address['totalCount']))
    else:
        module.fail_json(msg=result['msg'])
    
#RELEASE
    if module.params['minFreePublicIpv4Address'] < (publicIpList['totalPublicIp'] - reservedPublicIpv4Address['totalCount']):
        i = 0
        while i < publicIpList['totalCount']:
            b = True
            j = 0
            while j < reservedPublicIpv4Address['totalCount']:
                if reservedPublicIpv4Address['ip'][j]['ipBlockId']==publicIpList['publicIpBlock'][i]['id']: b = False
                j += 1
            if b and (module.params['minFreePublicIpv4Address'] <= (publicIpList['totalPublicIp'] - publicIpList['publicIpBlock'][i]['size'] - reservedPublicIpv4Address['totalCount'])):
                uri = '/caas/2.1/'+orgId+'/network/removePublicIpBlock'
                _data = {}
                _data['id'] = publicIpList['publicIpBlock'][i]['id']
                data = json.dumps(_data)
                if module.check_mode: 
                    has_changed=True
                else: 
                    result = caasAPI(caas_credentials, uri, data)
                    if not result['status']: module.fail_json(msg=result['msg'])
                    else: 
                        has_changed = True
                        publicIpList['totalPublicIp'] -= publicIpList['publicIpBlock'][i]['size']
            i += 1
    
#GET
    logging.debug("   minFreePublicIpv4Address/totalPublicIp/reservedPublicIpv4Address:"+str(module.params['minFreePublicIpv4Address'])+"/"+str(publicIpList['totalPublicIp'])+"/"+str(reservedPublicIpv4Address['totalCount']))
    while module.params['minFreePublicIpv4Address'] > (publicIpList['totalPublicIp'] - reservedPublicIpv4Address['totalCount']):
        uri = '/caas/2.1/'+orgId+'/network/addPublicIpBlock'
        _data = {}
        _data['networkDomainId'] = module.params['networkDomainId']
        data = json.dumps(_data)
        if module.check_mode: has_changed=True
        else: 
            result = caasAPI(caas_credentials, uri, data)
            if not result['status']: module.fail_json(msg=result['msg'])
            else: 
                has_changed = True
                publicIpList = _listPublicIpBlock(module,caas_credentials,orgId)

    module.exit_json(changed=has_changed, freePublicIpv4Address=publicIpList['totalPublicIp'] - reservedPublicIpv4Address['totalCount'], publicIpBlocks=publicIpList, reservedPublicIpv4Address=reservedPublicIpv4Address)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
