import json
import urllib
import requests

__author__ = 'Peleus Uhley'
__copyright__   = "Copyright 2015, Adobe System Incorporated"
__license__ = "MIT License"


class crits:
  """
  This class manages the interactions with the CRITs server via the API.
  """

  def __init__(self,username,api_key,crits_url,verify=True,debug=False):
    """
    The initialization class which stores the CRITs connection info.

    :param username: The user ID for the CRITs account.
    :type username: str
    :param api_key: The API key associated with the CRITs ID.
    :type api_key: str
    :param crits_url: The URL for the CRITs API.
    :type crits_url: str
    :param verify: Whether or not to verify the SSL certificate in an HTTPS connection.
    :type verify: bool
    :param debug: A boolean indicating whether to print debug statements.
    :type debug: bool
    """

    self.username = username
    self.api_key = api_key
    self.CRITs_URL = crits_url
    self.verify = verify
    self.debug = debug



  def find_campaign(self,name="",id="",limit=20,offset=0):
    """
    Finds the information associated with the given campaign.
    Depending on the type of error, this will either exit or return None.
    If successful, it will return a dict representing the JSON response.

    :param name: The name of the campaign to lookup.
    :type name: str
    :param id: The ID of the campaign to lookup.
    :type id: str
    :param limit: The max number of responses to return. Must be <= 1000
    :type limit: int
    :param offset: Which rows to return
    :type offset: int
    :returns: dict
    """

    url = self.CRITs_URL + 'campaigns/' 

    if id != None and id != "":
      url = url + str(id) + '/'

    url = url + '?username=' + self.username + '&api_key=' + self.api_key 

    if id == None or id == "":
      url =  url + '&' + urllib.urlencode({'c-name':name})

    if limit != None and limit != "":
      url = url + '&' + urllib.urlencode({'limit': str(limit)})

    if offset != None and offset != "":
      url = url + '&' + urllib.urlencode({'offset': str(offset)})

    try: 
      r = requests.get(url,verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "find_campaign error: Could not connect to " + url + "\n" + str(e.message)
      exit(1)
    except requests.exceptions.Timeout:
      print "find_campaign error: Timeout connecting to " + url
      exit(1)

    if r.status_code != 200:
      print "find_campagin error: Error code returned from the server: " + str(r.status_code)
      exit(1)

    j = json.loads(r.text)

    #if self.debug:
    #  print ">>>find_campaign response<<<"
    #  print j

    if id != None and id != "":
      return j
    else: 
      if j['meta']['total_count'] == 1:
        return j['objects']

    return None



  def add_campaign(self, name, description):
    """
    Add a campaign to the CRITs database.
    Depending on the error, this with either exit or return false.

    :param campaign: The campaign to add.
    :type campaign: str
    :param description: The description of the campaign
    :type description: str
    :returns: boolean
    """

    url = self.CRITs_URL + 'campaigns/'

    if name == None or name == "":
      print "A campaign name must be supplied to add_campaign!"
      exit(1)

    data = {
      'username' : self.username,
      'api_key' : self.api_key,
      'name' : name,
      'description' : description
    }

    try:
      r = requests.post(url, data=data, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "add_campaign error: Could not connect to " + url + "\n" + str(e.message)
      exit(1)
    except requests.exceptions.Timeout:
      print "add_campaign error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>add_campaign response<<<\n"
    #  print r.text

    if r.text != None and r.text != "":
      j = json.loads(r.text)
    else:
      j = {}


    if r.status_code == 200:
      if j['return_code'] == 1:
        print j['message']
        return False

      if self.debug:
        print "Successfully added "+ name

      return (True)

    elif self.debug:
       print name + " " + str(r.status_code)

    return (False)



  def find_domain(self,domain, campaign="", source="", id="", limit=20,offset=0):
    """
    Find a domain(s) within the CRITs database.
    If a domain value is not provided, then it will return all the domains in the campaign.
    Depending on the error, this will either exit or return None.
    The source variable currently isn't supported by CRITs.
    This will return a dict representing the domain's JSON response.

    :param domain: The name of the domain to lookup.
    :type domain: str
    :param campaign: A name of the campaign where the domain can be found.
    :type campaign: str
    :param source: The source of the domain.
    :type source: str
    :param id: The ID of the domain record.
    :type id: str
    :param limit: The max number of responses to return. Must be <= 1000.
    :type limit: int
    :param offset: For large responses, return rows starting after offset.
    :type offset: int
    :returns: dict
    """

    url = self.CRITs_URL + 'domains/' + '?username=' + self.username + '&api_key=' + self.api_key

    if id != None and id != "":
      url = url + str(id) + '/'

    url = url + '?username=' + self.username + '&api_key=' + self.api_key

    if domain != None and domain != "":
      url = url + '&' + urllib.urlencode({'c-domain': domain})

    if campaign != None and campaign != "":
      url = url + '&' + urllib.urlencode({'c-campaign.name': campaign})

    if source != None and source != "":
      url = url + '&' + urllib.urlencode({'c-source.name': source})

    if limit != None and limit != "":
      url = url + '&' + urllib.urlencode({'limit': str(limit)})

    if offset != None and offset != "":
      url = url + '&' + urllib.urlencode({'offset': str(offset)})

    try:
      r = requests.get(url, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "find_domain error: Could not connect to " + url + "\n" + str(e.message)
      exit(1)
    except requests.exceptions.Timeout:
      print "find_domain error: Timeout connecting to " + url
      exit(1)

    if r.status_code != 200:
      print "find_domain error: Error code returned from the server: " + str(r.status_code)
      exit(1)

    #if self.debug:
    #  print ">>>find_domain response<<<\n"
    #  print r.text

    j = json.loads(r.text)

    if id != None and id != "":
      return j
    else:
      if j['meta']['total_count'] >= 1:
        return j['objects']

    return None



  def add_domain(self, domain, campaign, source, indicator="false",confidence="low"):
    """
    Add a domain to the CRITs database.
    The provided values for source, confidence, etc. should match CRITs standards.
    Depending on the error, this with either exit or return false.

    :param domain: The domain to be added.
    :type domain: str
    :param campaign: The campaign under which the domain is filed.
    :type campaign: str
    :param source: The source for the given domain.
    :type source: str
    :param indicator: A boolean stating whether the domain is an indicator.
    :type indicator: boolean
    :param confidence: The confidence in the provided domain.
    :type confidence: str
    :returns: boolean
    """

    url = self.CRITs_URL + 'domains/'

    if domain == None or domain == "":
      print "A domain must be supplied to add_domain!"
      exit(1)

    data = {
      'username' : self.username,
      'api_key' : self.api_key,
      'source' : source,
      'campaign' : campaign,
      'domain' : domain,
      'confidence' : confidence
    }

    if indicator:
      data['add_indicator'] = indicator

    try:
      r = requests.post(url, data=data, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "add_domain error: Could not connect to " + url + "\n" + str(e.message)

      exit(1)
    except requests.exceptions.Timeout:
      print "add_domain error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>add_domain response<<<\n"
    #  print r.text

    if r.status_code == 200:
      j = json.loads(r.text)
      if j['return_code'] == 1:
        print j['message']
        return False
      if self.debug:
        print "Successfully added " + domain
      return True
    elif self.debug:
      print domain + " " + str(r.status_code)

    return (False)



  def find_ip(self,ip,campaign="",source="",id="", limit=20, offset=0):
    """
    Find an IP address within the CRITs database.
    If an IP value is not provided, then it will return all the IPs in the campaign.
    Depending on the error, this will either exit or return None.
    The source variable currently isn't supported by CRITs.
    This will return a dict representing the IP's JSON response.

    :param ip: The name of the IP to lookup.
    :type ip: str
    :param campaign: A name of the campaign where the IP can be found.
    :type campaign: str
    :param source: The source of the IP.
    :type source: str
    :param id: The GUID of the IP object.
    :type id: str
    :param limit: The max number of responses to return. Must be <= 1000.
    :type limit: int
    :param offset: For large responses, return rows starting after offset.
    :type offset: int
    :returns: dict
    """

    url = self.CRITs_URL + 'ips/'
 
    if id != None and id != "":
      url = url + str(id) + '/'

    url = url + '?username=' + self.username + '&api_key=' + self.api_key 

    if ip != None and ip != "":
      url = url + '&' + urllib.urlencode({'c-ip': ip})

    if campaign != None and campaign != "":
      url = url + '&' + urllib.urlencode({'c-campaign.name': campaign})

    if source != None and source != "":
      url = url + '&' + urllib.urlencode({'c-source.name': source})

    if limit != None and limit != "":
      url = url + '&' + urllib.urlencode({'limit': str(limit)})

    if offset != None and offset != "":
      url = url + '&' + urllib.urlencode({'offset': str(offset)})

    try: 
      r = requests.get(url, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "find_ip error: Could not connect to " + url + "\n" + str(e.message)
      exit(1)
    except requests.exceptions.Timeout:
      print "find_ip error: Timeout connecting to " + url
      exit(1)

    if r.status_code != 200:
      print "find_ip error: Error code returned from the server: " + str(r.status_code)
      exit(1)

    j = json.loads(r.text)

    #if self.debug:
    #  print ">>>find_ip response<<<"
    #  print r.text

    if id != None and id != "":
      return j
    else:
      if j['meta']['total_count'] >= 1:
        return j['objects']

    return None



  def add_ip(self,ip,campaign, source, ip_type="Address - ipv4-addr", indicator=False, confidence="low"):
    """
    Add an IP address to the CRITs database.
    The provided values for ip_type, confidence, etc. should match CRITs standards.
    Depending on the error, this with either exit or return false.

    :param ip: The IP to be added.
    :type ip: str
    :param campaign: The campaign under which the IP is filed.
    :type campaign: str
    :param source: The source for the given IP.
    :type source: str
    :param ip_type: The type of IP being provided ipv4, cidr, etc.
    :type ip_type: str
    :param indicator: A boolean stating whether the IP is an indicator.
    :type indicator: boolean
    :param confidence: The confidence in the provided IP.
    :type confidence: str
    :returns: A boolean indicating whether the submission was successful.
    """


    url = self.CRITs_URL + 'ips/'

    if ip == None or ip == "":
      print "An IP address must be supplied to add_ip!"
      exit(1)

    data = {
      'username' : self.username,
      'api_key' : self.api_key,
      'source' : source,
      'campaign' : campaign,
      'ip' : ip,
      'ip_type' : ip_type,
      'confidence' : confidence
    }

    if indicator:
      data['add_indicator'] = indicator

    try:
      r = requests.post(url, data=data, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "add_ip error: Could not connect to " + url + "\n" + str(e.message)
      exit(1)
    except requests.exceptions.Timeout:
      print "add_ip error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>add_ip response<<<\n"
    #  print r.text

    if r.status_code == 200:
      j = json.loads(r.text)

      if j['return_code'] == 1:
        print j['message']
        return False

      if self.debug:
        print "Successfully added " + ip

      return (True)

    elif self.debug:
      print ip + ": " + str(r.status_code)

    return (False)



  def delete_domain(self,d_id):
    """
    Deletes the domain associated with the supplied CRITs GUID.
    Depending on the type of error, the function will either exit or return False.

    :param d_id: The CRITs GUID for the domain to be deleted.
    :type d_id: str
    :returns: boolean
    """

    if d_id == None or d_id == "":
      print "A domain ID must be supplied to delete_domain!"
      exit(1)

    url = self.CRITs_URL + 'domains/' + d_id + '/' + '?username=' + self.username + '&api_key=' + self.api_key

    data = {} 

    try:
      r = requests.delete(url, data=data, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "delete_domain error: Could not connect to " + url
      exit(1)
    except requests.exceptions.Timeout as e:
      print "delete_domain error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>delete_domain response<<<\n"
    #  print r.text

    if r.text != None and r.text != "":
      j = json.loads(r.text)
    else:
      j = {}

    if r.status_code == 200:
      return_code = int(j['return_code'])
      if return_code == 0:
        if self.debug:
          print "Successfully deleted "+ d_id
        return (True)
      else:
        print "Error deleting " + d_id
        return (False)
    elif self.debug:
      print "Error with domain delete:" + d_id + " : " + str(r.status_code)

    return (False)



  def delete_domain_reference(self,d_id,source=""):
    """
    Deletes the source associated with a domain GUID.
    There must be 2 or more sources associated with the domain for this to work.
    Depending on the type of error, the function will either exit or return False.

    :param d_id: The CRITs GUID for the domain that will be modified.
    :type d_id: str
    :param source: The source to remove.
    :type source: str
    :returns: boolean
    """

    if d_id == None or d_id == "":
      print "A domain ID must be supplied to delete_domain_reference!"
      exit(1)

    if source == None or source == "":
      print "A source must be provided to delete_domain_reference."
      exit(1)

    url = self.CRITs_URL + 'domains/' + d_id + '/' + '?username=' + self.username + '&api_key=' + self.api_key

    data = {
      'source' : source,
      'id':d_id}

    try:
      r = requests.patch(url, data=json.dumps(data), verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "delete_domain_reference error: Could not connect to " + url
      print e
      exit(1)
    except requests.exceptions.Timeout as e:
      print "delete_domain_reference error: Timeout connecting to " + url
      print e
      exit(1)

    #if self.debug:
    #  print ">>>delete_domain_reference response<<<\n"
    #  print r.text

    if r.text != None and r.text != "":
      j = json.loads(r.text)
    else:
      j = {}

    if r.status_code == 200:
      return_code = int(j['return_code'])
      if return_code == 0:
        if self.debug:
          message = "Successfully updated "+ d_id
          if source != None and source != "":
            message += " and removed references to source: " + source
          print message
        return (True)
      else:
        print "Error with domain delete:" + d_id + " : " + str(r.status_code)
        return (False)
    elif self.debug:
      print "Error with domain delete:" + d_id + " : " + str(r.status_code)

    return (False)



  def delete_ip(self,ip_id):
    """
    Deletes the IP associated with the supplied CRITs GUID
    Depending on the type of error, the function will either exit or return False.

    :param ip_id: The CRITs GUID for the IP that will be deleted.
    :type ip_id: str
    :returns: boolean
    """

    if ip_id == None or ip_id == "":
      print "An IP ID must be supplied to delete_ip!"
      exit(1)

    url = self.CRITs_URL + 'ips/' + ip_id + '/' + '?username=' + self.username + '&api_key=' + self.api_key 

    data = {}

    try:
      r = requests.delete(url, data=data, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "delete_ip error: Could not connect to " + url
      exit(1)
    except requests.exceptions.Timeout:
      print "delete_ip error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>delete_ip response<<<\n"
    #  print r.text

    if r.status_code == 200:
      if self.debug:
        print "Successfully deleted "+ ip_id
      return (True)
    elif self.debug:
      print "Error with deleting IP GUID: " + ip_id + " : " + str(r.status_code)
      print r.text

    return (False)



  def delete_ip_reference(self,ip_id,source=""):
    """
    Deletes the source associated with an IP GUID.
    There must be two or more sources associated with the IP in order for this to work.
    Depending on the type of error, the function will either exit or return False.

    :param ip_id: The CRITs IP GUID that will be modified.
    :type ip_id: str
    :param source: The source that will be removed.
    :type source: str
    :returns: boolean
    """

    if ip_id == None or ip_id == "":
      print "An IP ID must be supplied to delete_ip_reference!"
      exit(1)

    if source == None or source == "":
      print "A source must be provided to delete_ip_reference."
      exit(1)

    url = self.CRITs_URL + 'ips/' + ip_id + '/' + '?username=' + self.username + '&api_key=' + self.api_key 

    data = {
      'source' : source,
      'id':ip_id}

    try:
      r = requests.patch(url, data=json.dumps(data), verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "delete_ip_reference error: Could not connect to " + url
      exit(1)
    except requests.exceptions.Timeout:
      print "delete_ip_reference error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>delete_ip_reference response<<<\n"
    #  print r.text

    if r.text != None and r.text != "":
      j = json.loads(r.text)
    else:
      j = {}

    if r.status_code == 200:
      return_code = int(j['return_code'])
      if return_code == 0:
        if self.debug:
          message = "Successfully updated "+ ip_id
          if source != None and source != "":
            message += " references to source: " + source
          print message
        return (True)
      else:
        print r.text
        return (False)
    elif self.debug:
      print "Error with IP patch: " + ip_id + " : " + str(r.status_code)
      print r.text

    return (False)



  def delete_campaign(self,c_id):
    """
    Deletes the Campaign associated with the supplied CRITs GUID.
    Depending on the type of error, the function will either exit or return False.

    :param c_id: The CRITs campaign GUID for deletion.
    :type c_id: str
    :returns: boolean
    """

    if c_id == None or c_id == "":
      print "A campaign ID must be supplied to delete_campaign!"
      exit(1)

    url = self.CRITs_URL + 'campaigns/' + c_id + '/' + '?username=' + self.username + '&api_key=' + self.api_key 

    data = {}

    try:
      r = requests.delete(url, data=data, verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "delete_campaign error: Could not connect to " + url
      exit(1)
    except requests.exceptions.Timeout:
      print "delete_campaign error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>delete_campaign response<<<\n"
    #  print r.text

    if r.status_code == 200:
      if self.debug:
        print "Successfully deleted "+ c_id
      return (True)
    elif self.debug:
      print "Error with campaign deletion: " + c_id + " : " + str(r.status_code)
      print r.text

    return (False)



  def delete_campaign_reference(self,campaign_id,obj_type,obj_id):
    """
    Deletes the data associated with a campaign_name.
    Depending on the type of error, the function will either exit or return False.

    :param campaign: The campaign to modify.
    :type campaign: str
    :param obj_type: The type of reference to remove ("IP","Domain").
    :type obj_type: str
    :param obj_id: The id of the obj_type that will be removed.
    :type obj_id: str
    :returns: boolean
    """

    if campaign_id == None or campaign_id == "":
      print "A campaign ID must be supplied to delete_campaign_reference!"
      exit(1)

    if obj_id == None or obj_id == "":
      print "An obj_id must be provided for the delete_campaign_reference update."
      exit(1)

    if obj_type == None or obj_type == "":
      print "An obj_type must be provided for the delete_campaign_reference update."
      exit(1)

    url = self.CRITs_URL + 'campaigns/' + str(campaign_id) + '/' + '?username=' + self.username + '&api_key=' + self.api_key 

    data = {
      'crits_type' : obj_type,
      'crits_id':obj_id}

    try:
      r = requests.patch(url, data=json.dumps(data), verify=self.verify)
    except requests.exceptions.ConnectionError as e:
      print "delete_campaign_reference error: Could not connect to " + url
      exit(1)
    except request.exceptions.Timeout:
      print "delete_campagin_reference error: Timeout connecting to " + url
      exit(1)

    #if self.debug:
    #  print ">>>delete_campaign_reference response<<<\n"
    #  print r.text

    if r.text != None and r.text != "":
      j = json.loads(r.text)
    else:
      j = {}

    if r.status_code == 200:
      return_code = int(j['return_code'])
      if return_code == 0:
        if self.debug:
          message = "Successfully updated campaign "+ campaign_id + " to remove " + obj_type + ": " + obj_id
          print message
        return (True)
      else:
        print r.text
        return (False)
    elif self.debug:
      print "Error with Campaign patch: " + campaign_id + " : " + str(r.status_code)
      print r.text

    return (False)
