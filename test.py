#Demo Test POC
import json
import base64
import urllib
import urllib2
import xml.etree.ElementTree as ET

def getOrgId(username,password):
  apiurl = 'https://api-eu.dimensiondata.com'
  apiuri = '/oec/0.9/myaccount'
  request = urllib2.Request(apiurl + apiuri)
  base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % base64string)
  response = urllib2.urlopen(request).read()

  root = ET.fromstring(response)
  ns = {'directory': 'http://oec.api.opsource.net/schemas/directory'}
  return root.find('directory:orgId',ns).text

def deployServer(username,password, orgId):
  apiurl = 'https://api-eu.dimensiondata.com'
  apiuri = '/caas/2.1/'+orgId+'/server/deployServer'
  data = '{"name":"Production FTPS Server","description":"This is the main FTPS Server","imageId":"02250336-de2b-4e99-ab96-78511b7f8f4b","start":true,"administratorPassword":"P$$ssWwrrdGoDd!" }'
  request = urllib2.Request(apiurl + apiuri, data)
  base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % base64string)
  request.add_header("Content-Type", "application/json")
  try:
    response = urllib2.urlopen(request)
    return response.read()
  except urllib2.HTTPError, e:
    print 'HTTPError = ' + e.read()
    return e.read()
