crits_scripts
===============

These are command line scripts for interacting with a CRITs API. The main script is os_list_update.py. It contains general functions for adding, deleting and retrieving information from the CRITs database.

The script can also download files from public IOC databases and sync the information with the CRITs server. The current list of supported IOC lists is in os_indicators.config. This script will download the current list, compare it with what is currently stored in CRITS for that campaign, and update accordingly.

The script is not compatible with all IOC lists. The compatibility of these scripts with an IOC list depends on the format of the list. Be sure to consult any terms or policies associated with the lists before using.


Required Python libraries:
  * import ConfigParser
  * import argparse
  * import sys
  * import re
  * import os.path
  * import gzip
  * import json
  * import urllib
  * import requests
  * from pprint import pprint
  * from sets import Set
  * from StringIO import StringIO


os_list_update.py
-------------------

 Local libraries
  * os_indicators.config -- Contains the list of supported open source feeds
  * crits.config -- Contains the defaults for interacting with CRITs
  * os_list_update.py -- The main command line utility
  * libs2/crits.py -- General class for interacting with the CRITs API

Example command lines:
  Note: Command line flags will override the values in the crits.config file.<br>
  In general, the scripts only return something if there is a failure.<br>

  Update the open-source Palevo list by adding new entries and deleting old ones (verbose mode). The script will use the os_indicators.config file to determine where to find the public Palevo information. If none of the defaults are changed, the IPs will be stored under the campaign, "OS-Palevo" from the source "Palevo". The source "Palevo" must exist in CRITs in order for this to work.<br>
  <i>./os_list_update.py --update_os_ip_list palevo -v </i>

  Import a local list of IPs from a file and add them to the campaign Campaign1 with the source OS-Source1. No entries will be removed.<br>
  <i>./os_list_update.py --import_ip_list filename.txt -c Campaign1 -s Source1 -v </i>
    
  Add the domain name example.org from Source1 into Campaign1 campaign with a confidence level of low. A campaign and source is mandatory.<br>
  <i>./os_list_update.py --add_domain_name example.org -c Campaign1 -c Source1 -l low </i>

  This will remove a source from a domain record.<br>
  <i>./os_list_update.py --delete_domain_info example.org -s Source1 </i>

  This will remove a campaign from a domain record.<br>
  <i>./os_list_update.py --delete_domain_info example.org -c Campaign1 </i>

  This will delete an entire domain record.<br>
  <i>./os_list_update.py --delete_domain_info example.org </i>

  This will remove a source from an IP record. If there is only one source, then it will delete the entire record.<br>
  <i>./os_list_update.py --delete_ip_info 127.0.0.1 -s Source1 </i>

  This will remove a campaign from an IP record.<br>
  <i>./os_list_update.py --delete_ip_info 127.0.0.1 -c Campaign1 </i>

  This will delete an entire IP record.<br>
  <i>./os_list_update.py --delete_ip_info 127.0.0.1 </i>

  Fetch information on the domain example.org.<br>
  <i>./os_list_update.py --get_domain_list -d example.org </i>

  Fetch all the domains associated with the campaign Campaign1.<br>
  <i>./os_list_update.py --get_domain_list -c Campaign1 </i>

  Get help.<br>
  <i>./os_list_update.py --help </i>
