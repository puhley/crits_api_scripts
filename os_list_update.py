#!/usr/local/bin/python
"""
This is a command line utility for interacting with a CRITs server API.

Before using this utility, ensure that crits.config contains your credentials.
The config file should be in the same directory as this script.

Any parameters passed on the command line will override the config file.

"""

__author__ = 'Peleus Uhley'
__copyright__   = "Copyright 2015, Adobe System Incorporated"
__license__ = "MIT License"


import ConfigParser
import argparse
import sys
import re
import requests
import os.path
import gzip
from pprint import pprint
from libs2 import crits
from sets import Set
from StringIO import StringIO


#The config file for the CRITs server
CRITS_CONFIG_FILE = 'crits.config'

#The config file containing the supported open source lists
OS_CONFIG_FILE = 'os_indicators.config'



def get_config_setting(Config,section,key,type='str'):
  """
  This is a utility function for reading variables from a config file.

  :param Config: The ConfigParser varialbe for the file containing the variable.
  :type Config: ConfigParser
  :param section: The section of the config file that contains the variable
  :type section: str
  :param key: The name of variable to read from the config file
  :type key: str
  :param type: The type of Config variable to read ('str','boolean',etc.)
               The default is 'str'
  :type type: str:
  :returns: str or boolean
  """
  try:
    if type == 'boolean':
      result = Config.getboolean(section,key)
    else:
      result = Config.get(section,key)
  except ConfigParser.NoSectionError as e:
    print 'Warning: ' + section + ' does not exist in config file'
    if type == 'boolean':
       return 0
    else:
       return ""
  except ConfigParser.NoOptionError as e:
    print 'Warning: ' + key + ' does not exist in the config file'
    if type == 'boolean':
       return 0
    else:
       return ""
  except ConfigParser.Error as e:
    print 'Warning: Unexpected error with config file'
    if type == 'boolean':
       return 0
    else:
       return ""

  return result





def download_file(url):
  """
  This will download and return the response body from the provided URL.

  :param url: The URL to use for the request.
  :type url: str
  :returns: str
  """
  try:
     r = requests.get(url, stream=True)
  except requests.exceptions.ConnectionError as e:
     print "Error: Could not connect to " + url
     exit(1)
  except requests.exceptions.Timeout:
     print "Error: Timeout connecting to " + url
     exit(1)

  if r.headers.get('content-encoding') == 'gzip':
     zipdata = StringIO()
     zipdata.write(r.raw.read())
     zipdata.seek(0)
     g = gzip.GzipFile(fileobj=zipdata, mode='rb')
     return(g)

  return (r.raw)




def get_crits_config(Config,args,debug):
  """
  Retrieve the CRITs connection info from the config file and/or command line.
  Returns the username, API key and URL

  :param Config: The ConfigParser varialbe for the file containing the variable.
  :type Config: ConfigParser
  :param args: The section of the config file that contains the variable
  :type args: :class:`argparse.Namespace`
  :param debug: A boolean indicating whether the debug flag is set.
  :type debug: boolean
  :returns: str, str, str
  """
  username = get_config_setting(Config,"CritsCreds","username")
  api_key = get_config_setting(Config,"CritsCreds","API_key")
  crits_url = get_config_setting(Config,"CritsCreds","CRITs_URL")

  if args.username:
     username = args.username
  if args.api_key:
     api_key = args.api_key
  if args.crits_url:
     crits_url = args.crits_url
   
  return username,api_key,crits_url



def get_indicator(Config,args,debug):
  """
  Retrieve the indicator setting from the config file and/or command line.
  Return a boolean regarding whether to add as an indicator.

  :param Config: The ConfigParser variable for the file containing the variable.
  :type Config: ConfigParser
  :param args: The section of the config file that contains the variable
  :type args: :class:`argparse.Namespace`
  :param debug: A boolean indicating whether the debug flag is set.
  :type debug: boolean
  :returns: boolean
  """
  indicator = get_config_setting(Config,"DefaultIndicatorInfo","add_indicator")

  if args.add_indicator:
    indicator = args.add_indicator

  if indicator == None:
    return (False)

  if (indicator != "True" and indicator != "False"):
     print "Error: The indicator is a boolean and can only be 'True' or 'False'"
     exit(1)
  elif indicator == "True":
     return (True)

  return(False)



def get_confidence(Config,args,debug):
  """
  Retrieve the confidence setting from the config file and/or command line.
  Return a string containing the confidence level.

  :param Config: The ConfigParser variable for the file containing the variable.
  :type Config: ConfigParser
  :param args: The section of the config file that contains the variable
  :type args: :class:`argparse.Namespace`
  :param debug: A boolean indicating whether the debug flag is set.
  :type debug: boolean
  :returns: str
  """
  confidence = get_config_setting(Config,"DefaultIndicatorInfo","confidence_level")

  if args.confidence_level:
    confidence = args.confidence_level

  if confidence == None:
    return("low")

  if (confidence != "low" and confidence != "medium" and confidence != "high"):
     print "Error: Confidence level must be 'low', 'medium', or 'high'"
     exit(1)

  return(confidence)




def get_campaign(Config,args,debug):
  """
  Retrieve the campaign setting from the config file and/or command line.
  Return the string containing the campaign name

  :param Config: The ConfigParser variable for the file containing the variable.
  :type Config: ConfigParser
  :param args: The section of the config file that contains the variable
  :type args: :class:`argparse.Namespace`
  :param debug: A boolean indicating whether the debug flag is set.
  :type debug: boolean
  :returns: str
  """
  campaign = get_config_setting(Config,"DefaultIndicatorInfo","campaign_name")

  if args.campaign:
    campaign = args.campaign

  if campaign == None:
    return("")

  return (campaign)




def get_source(Config,args,debug):
  """
  Retrieve the source setting from the config file and/or command line.
  Return a string specifying the source name.

  :param Config: The ConfigParser variable for the file containing the variable.
  :type Config: ConfigParser
  :param args: The section of the config file that contains the variable
  :type args: :class:`argparse.Namespace`
  :param debug: A boolean indicating whether the debug flag is set.
  :type debug: boolean
  :returns: str
  """
  source = get_config_setting(Config,"DefaultIndicatorInfo","source")

  if args.source:
    source = args.source

  if source == None:
    return("")

  return (source)




def get_ip_and_type(line):
  """
  This function will take a line from an open source file.
  It extracts the IP relevant information (either an IP address or CIDR class)
  It will return the IP value and the type of value('Address - cidr','Address - ipv4-addr') 

  :param A line containing an IP address or CIDR address class.
  :type line: str
  :returns: str, str
  """
  ip_result = re.match("^[0-9.]+([/0-9]+)?",line)

  if ip_result == None:
    return (None,None)

  ip = ip_result.group(0)

  if ip.find("/") != -1:
    return (ip,"Address - cidr")

  return (ip,"Address - ipv4-addr")




def get_section(f, first_delim, second_delim):
  """
  Some open-source indicator downloads contain multiple sections.
  This will return the section of the file f that is between the first_delim and second_delim

  :param f: The file containing the section to be processed
  :type f: file
  :param first_delim: A string representing the beginning of the section
  :type first_delim: str
  :param second_delim: A string representing the terminator of the section
  :type second_delim: str
  :returns: list
  """
  g = []

  line = f.readline()

  while line.find(first_delim) == -1:
    line = f.readline()

  line = f.readline()
  if second_delim != "":
    while line.find(second_delim) == -1:
      g.append(line)
      line = f.readline()
  else:
    for line in f:
      g.append(line)

  return(g)




def process_file(crits,file,campaign,source,indicator,confidence,debug):
  """
  Takes the list of lines from the provided file and inserts them into the database.
  The campaign, source, indicator and confidence settings will be used for each entry.
  This returns the set of ips from the file regardless of whether they were inserted.
  The set can be passed to remove_expired_entries to compare with the database records.

  :param crits: The CRITs class to be used for connecting
  :type crits: :class:`libs2\crits`
  :param file: The list of lines from the file
  :type file: list
  :param campaign: The string containing the campaign name to use.
  :type campaign: str
  :param source: The string representing the CRITs source. It must already exist.
  :type source: str
  :param indicator: The boolean representing whether or not these are indicators.
  :type indicator: boolean
  :param confidence: The string representing the confidence to use.
  :type confidence: str
  :param debug: A boolean indicating whether the debug flag is set.
  :type debug: boolean
  :returns: Set, Set
  """
  new_set = Set([])
  existing_set = Set([])
  current_entries = ['foo']
  limit = 1000
  offset = 0

  while current_entries != None and bool(current_entries):
    current_entries = crits.find_ip("",campaign,source,"",limit,offset)

    if current_entries != None:
      for result in current_entries:
        c_ip = result['ip']
        existing_set.add(c_ip)

    offset += 1000

  for line in file:
    line = line.strip()
    ip, ip_type = get_ip_and_type(line)
    if ip != None:
      new_set.add(ip)

  new_adds = new_set.difference(existing_set)

  if debug:
    print "Existing IP count: " + str(len(existing_set))
    print "File IP count: " + str(len(new_set))
    print "New additions: " + str(len(new_adds))

  for entry in new_adds:
    #This is a little weird since I asked for the type previously and threw it away
    e_ip,e_type = get_ip_and_type(entry)

    if crits.add_ip(e_ip,campaign,source,e_type,indicator,confidence) == False:
      print "Error adding IP address " + line + " in campaign: " + campaign
      exit(1)

  return(new_set,existing_set)



def find_campaign_source(result, args):
  """
  This is used by the delete functionality to determine whether to delete an entire record.
  If there is only one entry in result, it returns two blank strings so that the entire record  will be deleted.
  If there is more than one entry, it will verify the campaign and source exist and then return those values.

  :param result: The returned value from a CRITs find query.
  :type result: arr
  :param args: The args array from the command line
  :type args: object
  :returns: str,str
  """
  del_campaign = ""

  if len(result[0]['campaign']) >= 1 and args.campaign:
    for entry in result[0]['campaign']:
      if entry['name'] == args.campaign:
        del_campaign = args.campaign

    if del_campaign == "":
      print "Error: The campaign " + args.campaign + " is not associated with that IP."
      exit(1)


  #There must always be one source associated with a record
  del_source = ""
  if len(result[0]['source']) > 1 and args.source:
    for entry in result[0]['source']:
      if entry['name'] == source:
        del_source = source

    if del_source == "":
      print "Error: The source " + args.source + " is not associated with that IP."
      exit(1)

  return (del_campaign, del_source)



def remove_expired_entries(crits,campaign,source,in_set,existing_set,debug):
  """
  This will download all the IPs from the CRITs database for the given campaign.
  It will then take that set of IPs and diff them with the IPs in in_set.
  IPs that exist in the CRITs database but not within in_set are considered expired.
  Any IPs that were in the database that are not in in_set, are removed from the database.

  :param crits: The CRITs class to be used for connecting
  :type crits: :class:`libs2\crits`
  :param campaign: The string containing the campaign name that is being processed.
  :type campaign: str
  :param source: The string representing the CRITs source. It must already exist.
  :type source: str
  :param in_set: The set of IPs from the OS IP list
  :type in_set: Set
  :param existing_set: The set of IPs from the CRITs database
  :type existing_set: Set
  :param debug: A boolean indicating whether the debug flag is set.
  :type debug: boolean
  """

  expired_set = existing_set.difference(in_set)

  if debug:
    print "Expired set count: " + str(len(expired_set))

  for entry in expired_set:
    ip_result = CRITs.find_ip(entry)

    if ip_result == None:
      print "Error could not find the IP: " + entry + " in campaign: " + campaign
      exit(1)

    ip_id = ip_result[0]['_id']

    del_campaign=""
    if len(ip_result[0]['campaign']) > 1:
      del_campaign=campaign

    del_source=""
    if len(ip_result[0]['source']) > 1:
      del_source=source

    print "Deleting ip_id: " + ip_id + " campaign: " + del_campaign + " source: " + del_source

    if del_campaign == "" and del_source == "":
      result = CRITs.delete_ip(ip_id)
    else:
      if del_source != "":
        result = CRITs.delete_ip_reference(ip_id,del_source)
        if not result:
          print "There was an error deleting the source!"
          exit(1)
      if del_campaign != "":
        campaign_result = CRITs.find_campaign(del_campaign)
        if campaign_result == None:
          print "Error: Could not find the campaign: " + del_campaign
          exit(1)
        campaign_id = campaign_result[0]['_id']
        result = CRITs.delete_campaign_reference(campaign_id,"IP",ip_id)

    if not result:
      print "Error: Could not delete IP: " + ip_id


if __name__ == '__main__':
  if sys.version_info[0] >= 3:
     print 'This script currently only supports Python version 2.x'
     exit(1)


  parser = argparse.ArgumentParser(description='A utility for interacting with CRITs APIs')


  parser.add_argument('-u','--username', 
                   help='The username of the CRITs user associated with the api_key')
  parser.add_argument('-k','--api_key',
                   help='The API key of the CRITs user')
  parser.add_argument('-a','--crits_url',
                   help='The URL of the CRITs API')
  parser.add_argument('-c','--campaign',
                   help='The campaign name to use for the query')
  parser.add_argument('-cd','--description',
                   help='The description to go along with the new campaign')
  parser.add_argument('-i','--ip',
                   help='The ip address to use for the query')
  parser.add_argument('-d','--domain',
                   help='The domain name to use for the query')
  parser.add_argument('-id','--id',
                   help='The id # to use for the query')
  parser.add_argument('-s','--source',
                   help='The source to use for the query')
  parser.add_argument('-n','--add_indicator',
                   help='A boolean value ("True"/"False") for whether to add it as an indicator')
  parser.add_argument('-l','--confidence_level',
                   help='The confidence level for an IP or domain. Must be "low","medium", or "high"')
  parser.add_argument('-v','--verbose', action='store_true',
                   help='Enable verbose output for debugging')
  parser.add_argument('--config_file', default=CRITS_CONFIG_FILE,
                   help='The CRITS configuration file to use')
  parser.add_argument('--os_config_file', default=OS_CONFIG_FILE,
                   help='The open source configuration file to use')


  group = parser.add_mutually_exclusive_group()
  group.add_argument('--get_ip_list', action='store_true',
                   help='Get IP address information from CRITs')
  group.add_argument('--add_ip_address', 
                   help='Add the IP address to CRITs')
  group.add_argument('--delete_ip_info',
                   help='Delete IP address information from CRITs')
  group.add_argument('--delete_ip_id',
                   help='Delete the IP assocaited with the GUID from CRITs')
  group.add_argument('--get_domain_list', action='store_true',
                   help='Get domain name information from CRITs')
  group.add_argument('--add_domain_name',
                   help='Add the domain info to CRITs')
  group.add_argument('--delete_domain_info',
                   help='Delete domain information from CRITs')
  group.add_argument('--delete_domain_id',
                   help='Delete the domain associated with the GUID from CRITs')
  group.add_argument('--get_campaign_list', action='store_true',
                   help='Get campaign information from CRITs')
  group.add_argument('--add_campaign', 
                   help='Add the campaign name to CRITs')
  group.add_argument('--delete_campaign', 
                   help='Delete the campaign from CRITs')
  group.add_argument('--import_ip_list',
                   help='Import a file containing a list of IPs')
  group.add_argument('--update_os_ip_list',
                   help='Download and update the specified list of open source IPs')
  args = parser.parse_args()


  Config = ConfigParser.ConfigParser()
  list = Config.read(args.config_file)
  if len(list) == 0:
     print 'Error: Could not find the crits.config file'
     exit(1)

  OSConfig = ConfigParser.ConfigParser()
  os_list = OSConfig.read(args.os_config_file)
  if len(os_list) == 0:
     print 'Error: Could not find the os_indicators.config file'
     exit(1)


  verify = get_config_setting(Config,'General','verify','boolean')

  debug = get_config_setting(Config,'General','debug','boolean')
  if args.verbose:
     debug = True
  
  #Get the CRITs connection info and initialize a CRITs object.
  username,api_key,crits_url = get_crits_config(Config,args,debug)
  CRITs = crits.crits(username,api_key,crits_url,verify,debug)


  #Get the default settings for the process
  confidence = get_confidence(Config,args,debug)
  indicator = get_indicator(Config,args,debug)
  campaign = get_campaign(Config,args,debug)
  source = get_source(Config,args,debug)

  campaign_prefix = get_config_setting(OSConfig,'General','open_source_campaign_prefix')


  #Fetch IP information from CRITs based on an IP, campaign or source.
  if args.get_ip_list:
    ip_result = CRITs.find_ip(args.ip,campaign,source,args.id)

    if ip_result == None:
      message = "IP not found."
      if campaign:
         message += " Campaign: " + campaign
      if args.ip:
         message += " IP: " + args.ip
      print message

    else:
      pprint(ip_result)

    exit(0)



  #Add a single IP address to CRITs under the given campaign
  if args.add_ip_address:
    if source == None or source == "":
      print "Please provide a source for the IP using -s"
      exit(1)

    if campaign == None or campaign == "":
      print "Please provide a campaign for the IP using -c"
      exit(1)

    ip,ip_type = get_ip_and_type(args.add_ip_address)
    ip_result = CRITs.add_ip(ip,campaign,source,ip_type)

    if ip_result == False:
      print "Error could not add IP address: " + ip + "!"
      exit(1)

    exit(0)



  #Fetch domain information from CRITs based on the domain, source or campaign.
  if args.get_domain_list:
    domain_result = CRITs.find_domain(args.domain,campaign,source,args.id)

    if domain_result == None:
      message = "Domain Not Found."

      if campaign:
        message += " Campaign: " + campaign
      if args.domain:
        message +=  " Domain: " + args.domain
      print message

    else:
      pprint(domain_result)

    exit(0)



  #Add a single domain to CRITs under the given campaign
  if args.add_domain_name:
    if source == None or source == "":
      print "Error: Please provide a source for the domain using -s"
      exit(1)

    if campaign == None or campaign == "":
      print "Error: Please provide a campaign for the domain using -c"
      exit(1)

    domain_result = CRITs.add_domain(args.add_domain_name,campaign,source)
    if domain_result == False:
      print "Error: Could not add domain: " + args.add_domain_name + "!"
      exit(1)
    exit(0)



  #Fetch the information on the given campaign from CRITs
  if args.get_campaign_list:
    campaign_result = CRITs.find_campaign(campaign, args.id)
    if campaign_result == None:
      print "Campaign Not Found!"
    else:
      pprint(campaign_result)
    exit(0)



  #Add a new campaign to CRITs
  if args.add_campaign:
    campaign_result = CRITs.add_campaign(args.add_campaign,args.description)
    if campaign_result:
      print "Campaign successfully added"
    else:
      print "Error adding campaign: " + args.add_campaign
      exit(1)

    exit(0)



  #Import a list of IPs from a command line provided file
  if args.import_ip_list:
    if source == None or source == "":
      print "Error: Please supply a source using -s"
      exit(1)

    if campaign == None or campaign == "":
      print "Error: Please supply a campaign using -c"
      exit(1)

    if os.path.isfile(args.import_ip_list) == False:
      print "Error: The supplied file name does not exist!"
      exit(1)

    with open(args.import_ip_list,'r') as f:
      process_file(CRITs,f,campaign,source,indicator,confidence,debug)

    exit(0)



  #Download and process an open source list specified in the os_indicators.config.
  if args.update_os_ip_list:
    os_list_name = args.update_os_ip_list

    os_source = get_config_setting(OSConfig,'Open Source Lists',os_list_name + '_source')
    os_url = get_config_setting(OSConfig,'Open Source Lists',os_list_name + '_URL')

    if os_source == None or os_source == "":
      print "Error: Could not identify the source attribute in the config file for " + os_list_name
      exit(1)

    if os_url == None or os_url == "":
      print "Error: Could not identify the url attribute in the config file for " + os_list_name
      exit(1)
 
    f = download_file(os_url)

    g = f

    if os_list_name == "shadowserver":
      shadow_begin = get_config_setting(OSConfig,'Open Source Lists','shadowserver_begin')

      spamhaus_begin = get_config_setting(OSConfig,'Open Source Lists','spamhaus_begin')
      g = get_section(f,shadow_begin,spamhaus_begin)

    elif os_list_name == "spamhaus":
      spamhaus_begin = get_config_setting(OSConfig,'Open Source Lists','spamhaus_begin')
      dshield_begin = get_config_setting(OSConfig,'Open Source Lists','dshield_begin')
      g = get_section(f,spamhaus_begin,dshield_begin)

    elif os_list_name == "dshield":
      dshield_begin = get_config_setting(OSConfig,'Open Source Lists','dshield_begin')
      g = get_section(f,dshield_begin,"")
    elif os_list_name == "alienvault":
      zipdata = StringIO()
      zipdata.write(f.read())
      zipdata.seek(0)
      g = gzip.GzipFile(fileobj=zipdata, mode='rb')

    os_campaign_prefix = get_config_setting(OSConfig,'General', 'open_source_campaign_prefix')
    os_add_campaign = get_config_setting(OSConfig,'General', 'add_campaign_if_missing','boolean')


    os_campaign = campaign
    if args.campaign == None or args.campaign == "":
      os_campaign = os_campaign_prefix + os_source


    campaign_exists = CRITs.find_campaign(os_campaign)
    if campaign_exists == None and os_add_campaign:
      print "Warning! Campaign does not exist! Adding new campaign: " + os_campaign
      CRITs.add_campaign(os_campaign, "Open source IP list from " + os_source)

    elif campaign_exists == None:
      print "Error: Campaign does not exist! Aborting!"
      exit(1)


    if debug:
      print "Processing file..."
    in_set,existing_set = process_file(CRITs,g,os_campaign,os_source,indicator,confidence,debug)

    if debug:
      print "Removing old entries..."
    remove_expired_entries(CRITs,os_campaign,os_source,in_set,existing_set,debug)
    exit(0)




  #Delete an entire IP address info or IP attributes from the CRITs server.
  if args.delete_ip_info:

    ip_result = CRITs.find_ip(args.delete_ip_info,campaign,source)

    if ip_result == None:
      print "Error: Could not find the IP: " + args.delete_ip_info
      if campaign != None and campaign == "":
        print "in campaign: " + campaign
      exit(1)

    ip_id = ip_result[0]['_id']

    if ip_id == None:
      print "Error: Could not get _id for " + args.ip
      exit(1)

    del_campaign,del_source = find_campaign_source(ip_result,args)

    if debug:
      print "Deleting IP ID: " + ip_id + " campaign: " + del_campaign + " source: " + del_source

    if del_campaign == "" and del_source == "":
      result = CRITs.delete_ip(ip_id)

    else:
      if del_source != "":
        result = CRITs.delete_ip_reference(ip_id,del_source)
        if not result:
          print "There was an error deleting the source!"
          exit(1)

      if del_campaign != "":
        campaign_result = CRITs.find_campaign(del_campaign)
        if campaign_result == None:
          print "Error: Could not find the campaign: " + del_campaign
          exit(1)
        campaign_id = campaign_result[0]['_id']
        result = CRITs.delete_campaign_reference(campaign_id,"IP",ip_id)

        if not result:
          print "There was an error deleting the campaign!"
          exit(1)
    exit(0)



  #Delete either an entire domain or domain attributes from the CRITs server.
  if args.delete_domain_info:

    domain_result = CRITs.find_domain(args.delete_domain_info,campaign,source)

    if domain_result == None:
      print "Error: Could not find the domain: " + args.delete_domain_info
      if campaign != None and campaign != "":
        print " in campaign: " + campaign
      exit(1)

    d_id = domain_result[0]['_id']

    if d_id == None:
      print "Error: Could not get _id for " + args.delete_domain_info
      exit(1)

    del_campaign,del_source = find_campaign_source(domain_result,args)

    if debug:
      print "Deleting Domain ID: " + d_id + " campaign: " + del_campaign + " source: " + del_source

    if del_campaign == "" and del_source == "":
      result = CRITs.delete_domain(d_id)

    else:
      if del_source != "":
        result = CRITs.delete_domain_reference(d_id,del_source)

        if not result:
          print "There was an error deleting the source from the domain!"
          exit(1)

      if del_campaign != "":
        campaign_result = CRITs.find_campaign(del_campaign)
        if campaign_result == None:
           print "Error: Could not find the campaign: " + del_campaign
           exit(1)
        campaign_id = campaign_result[0]['_id']
        result = CRITs.delete_campaign_reference(campaign_id,"Domain",d_id)

        if not result:
          print "There was an error deleting the campaign from the domain!"
          exit(1)

    exit(0)



  #Delete an entire campaign based on its name
  if args.delete_campaign:
    campaign_result = CRITs.find_campaign(args.delete_campaign)

    if campaign_result == None:
      print "Error: Could not find the campaign: " + del_campaign
      exit(1)

    campaign_id = campaign_result[0]['_id']
    result = CRITs.delete_campaign(campaign_id)

    if not result:
      print "There was an error deleting the campaign!"
      exit(1)

    exit(0)



  #Delete a specific domain based on its GUID
  if args.delete_domain_id:
    result = CRITs.delete_domain(args.delete_domain_id)

    if not result:
      print "There was an error deleting domain ID!"
      exit(1)

    exit(0)



  #Delete a specific IP based on its GUID
  if args.delete_ip_id:
    result = CRITs.delete_ip(args.delete_ip_id)

    if not result:
      print "There was an error deleting the IP ID!"
      exit(1)

    exit(0)


exit(0)
