'''
Created on Mar 20, 2016

@author: morriszeitouni
'''
import requests
import csv
import json
import datetime
import time
import xml.etree.ElementTree as ET
#import numpy as np
#from scipy.stats import norm, mode
#from datetime import timedelta
#import traceback
import logging
#import os.path
#import dateutil.parser as dparser
#from django.utils.timezone import utc
import pdb
import dateutil.parser as dparser
#from gunicorn.http.wsgi import Response
#try:
#    import http.client as http_client
#except ImportError:
#    # Python 2
#    import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1

# Constants

SANDBOX_URL = 'https://api.stubhubsandbox.com'
PROD_URL = 'https://api.stubhub.com'

USERNAME = 'abelabo30@aol.com'
PASSWORD = 'nyjets'
BASIC_AUTH_SAND = 'NGJ6Z2Z5TVlFZVFZekZTWDlUQkhzbmlBdk5BYTpTQWluVzQ3Nk9xYnRfc1J4eXhWQTZodTFzb3Nh'
APP_TOKEN_SAND = 'fgl8uH5CdfRJH7dXyazfEwnFf3ka'
BASIC_AUTH_PROD = 'TlczU0ZMbVgycXNEenp1S3IzOGdkdExHbnlrYTpBVHhib3pJSjhsS3A5TnJQcVROdXZraGloREVh'
APP_TOKEN_PROD = 'He3oVj6yqxvkHfSB8Rd7rAL0tvAa'

#Specify keys to use - Sandbox or Prod
BASIC_AUTH = BASIC_AUTH_PROD
APP_TOKEN = APP_TOKEN_PROD
URL = PROD_URL
cache = {}

def req(full_url, headers, params, req_type='GET', use_cache=True):
   cache_key = str(full_url) + str(headers) + str(params) + str(req_type)
   if use_cache and (cache_key in cache):
       return cache[cache_key]
  # print "Request:", full_url, headers, params, req_type
   response = None
   
   if req_type == 'GET':
       response = requests.get(full_url, headers=headers, params=params)
   elif req_type == 'POST':
               
#        logging.basicConfig() 
#        logging.getLogger().setLevel(logging.DEBUG)
#        requests_log = logging.getLogger("requests.packages.urllib3")
#        requests_log.setLevel(logging.DEBUG)
#        requests_log.propagate = True
#       pdb.set_trace()
       response = requests.post(full_url, headers=headers, data=params)
   elif req_type == 'PUT':
       #import pdb; pdb.set_trace()
       response = requests.put(full_url, headers=headers, data=json.dumps(params))
   elif req_type == 'DELETE':
       response = requests.delete(full_url, headers=headers, params=params)
   else:
       return None
   #pdb.set_trace()
 #  print response.json()
  # import pdb; pdb.set_trace()
   cache[cache_key] = response
   return cache[cache_key]


def login(basic_auth=BASIC_AUTH, username=USERNAME, password=PASSWORD, base_url=URL):
   headers = {'Content-Type': 'application/x-www-form-urlencoded',
              'Authorization': 'Basic %s' % (basic_auth),
              }

   params = {
       'grant_type': 'password',
       'username': username,
       'password': password,
       'scope': 'PRODUCTION'
   }
  
   return req(full_url='%s/login' % (base_url), headers=headers, params=params, req_type='POST')

class Stubhub():
    @staticmethod
    def get_app_token(app_token=APP_TOKEN):
       return app_token

    @staticmethod
    def get_user_token(basic_auth=BASIC_AUTH, username=USERNAME, password=PASSWORD, base_url=URL):
       return login(basic_auth=basic_auth, username=username, password=password, base_url=base_url).json()[
           'access_token']

    @staticmethod
    def get_user_id(basic_auth=BASIC_AUTH, username=USERNAME, password=PASSWORD, base_url=URL):
        return login(basic_auth=basic_auth, username=username, password=password, base_url=base_url).headers[
            'X-StubHub-User-GUID']

    def __init__(self, app_token, user_token, user_id):
        self.app_token = app_token
        self.user_token = user_token
        self.user_id = user_id

    def send_req(self, url, token_type='USER', req_type='GET', headers=None, params=None, use_cache=False):
        token = self.user_token if token_type == 'USER' else self.app_token
        params = params or {}
     #   pdb.set_trace()
        
        headers = headers or {'Authorization': 'Bearer %s' % (token), 'Content-Type': 'application/json'}
        
       # pdb.set_trace()
        full_url = '%s%s' % (URL, url)
        #print full_url, params, headers

        return req(full_url=full_url, headers=headers, params=params, req_type=req_type, use_cache=use_cache)

    def get_event(self, event_id):
        return self.send_req('/catalog/events/v2/%s' % (event_id), token_type='APP')

    def get_event_inventory(self, event_id, start=0, rows=10000, zonestats=True, sectionstats=True):
        params = {'eventId': event_id,'sort':'currentprice', 'start': start, 'rows': rows, 'zonestats' : zonestats, 'sectionstats' : sectionstats}
        return self.send_req('/search/inventory/v1', token_type='USER', req_type='GET', params=params).json()
    
    def get_event_inventory_v2(self, event_id, start=0, rows=10000, zonestats=True, sectionstats=True):
        params = {'eventId': event_id, 'start': start, 'rows': rows, 'zonestats' : zonestats, 'sectionstats' : sectionstats}
        
        return self.send_req('/search/inventory/v2/', token_type='USER', req_type='GET', params=params)

    def get_other_listing(self, listing_id):
        
        return self.send_req('/inventory/listings/v1/%s' % (listing_id), token_type='APP').json()
    
    def get_all_my_listings(self):
        
        return self.send_req('/accountmanagement/listings/v1/seller/%s' %self.user_id, token_type='USER', req_type='GET' ).json()
    
    def get_my_listing(self,listing_id):
        
        return self.send_req('/accountmanagement/listings/v1/%s' %listing_id, token_type='USER', req_type='GET' ).json()
    
    def get_sales(self):

      return self.send_req('/accountmanagement/sales/v1/seller/%s' %self.user_id, token_type='USER', req_type='GET').json()

    def change_price(self, listing_id, new_price):
        
        params = {"pricePerProduct" : {"amount": new_price, "currency": "USD"}}
        
        return self.send_req('/inventory/listings/v2/%s' %listing_id, token_type = 'USER',  req_type='PUT', params = params).json()

#         params = {"listing": {'pricePerTicket': new_price}}
#         return self.send_req('/inventory/listings/v1/%s' % (listing_id), token_type='USER', req_type='PUT', params=params).text

    # This function doesnt work - I need it to return a list of games for that team
    # API found here - https://developer.stubhub.com/store/site/pages/doc-viewer.jag?category=Search&api=EventSearchAPIv2&endpoint=searchforeventsv2&version=v2
    def get_team_games(self, team):
        #performer_id = get_performer_id(event_id)
        
        params = {'name': team, 'parking': False, 'start': 0, 'limit':500}
        response = self.send_req('/search/catalog/events/v3', token_type='APP',req_type='GET', params=params).json()
        #pdb.set_trace()
        #print team
        #print response
       
        events = response['events']
        
        #pdb.set_trace()
        #print "%s: %s" %(team, events)
        
        ids =[]
        venues = []
        i=1
        for event in events:
            try:
                #print "%s: %s" %(i,event['venue']['name'])
                venues.append(event['venue']['name'])
                i+=1
            except:
                #print event
                print "Index out of range"
        home_field = max(set(venues), key=venues.count)

     #   print home_field
        ids_dates = {}
        ids_opponents = {}
        for event in events:
            if event['venue']['name'] == home_field:
                
                ids_dates[event['id']] = dparser.parse(event['eventDateLocal'])
                #pdb.set_trace()
                try:
                    ids_opponents[event['id']] = event['groupingsCollection'][2]['name'].replace(" Road Games", "")
                except:
                    print "Couldn't get opponent"
        return ids_dates, ids_opponents
    def check_date(self, event_id):
    
        # Get XML of event details
        event_details = self.get_event(event_id=event_id).text
        root = ET.fromstring(event_details)
        #root = ET.fromstring(unicode(event_details.decode('utf-8')))
        event_date_UTC_unformatted = root[7].text
        event_date_UTC = datetime.datetime.strptime(event_date_UTC_unformatted[:10] , '%Y-%m-%d')
    
        now = datetime.datetime.now()
    
        if event_date_UTC > now:
            return True
        else:
            return False

    def create_listing(self, listing_dict):

        #params = listing_dict
#         params = {         
#             "eventId": "9445175",
#             "pricePerProduct": {"amount": "503", "currency": "USD"},
#             "quantity": "1",
#             "splitOption": "NOSINGLES",
#             "deliveryOption": "BARCODE",
#             "section": "311",
#             "products":{"row":"4", "seat":"12", "operation": "ADD", "productType": "TICKET"}
#         }
        eventId = listing_dict['eventId']
        quantity = listing_dict['quantity']
        section = listing_dict['section']
        row = listing_dict['row']
        splitOption = 'NOSINGLES'
        deliveryOption = 'BARCODE'
        quantity = int(listing_dict['quantity'])
        price = listing_dict['price']
       # pdb.set_trace()
        tickets = ''
        counter = 0
        print 'im here'
        if 'seats' not in listing_dict:
            for seat in range (0,quantity):
                addition = ''
                if counter != 0:
                    addition = ","
                tickets = tickets + addition + "{\"row\":\"%s\", \"operation\": \"ADD\", \"productType\": \"ticket\"}" %(row)
                counter+=1
            
            
        else:
            for seat in listing_dict['seats']:
                addition = ''
                if counter != 0:
                    addition = ","
                tickets = tickets + addition + "{\"row\":\"%s\", \"seat\":\"%s\", \"operation\": \"ADD\", \"productType\": \"ticket\"}" %(row, seat)
                counter+=1
            
        print tickets
       # pdb.set_trace()
        #price = (float(self.get_cheapest(eventId, section))) * 1.05

        params = " {\n\"eventId\": \"%s\",\n \"pricePerProduct\": {\"amount\": \"%s\", \"currency\": \"USD\"},\n\"quantity\": %d,\n\"splitOption\": \"%s\",\n \"deliveryOption\": \"%s\",\n\"section\": \"%s\",\n\"products\":[%s]\n}" %(eventId, price, quantity, splitOption, deliveryOption, section, tickets)


        print params
        response = self.send_req('/inventory/listings/v2', token_type='USER', req_type='POST',params = params)
        #pdb.set_trace()
        #stubhub_id = response.json()['id']
        return response.json()
    
    def create_listing_with_barcodes(self):
        
        params = {
                  "listing": {
                    "event": "9445175",
                    "pricePerTicket": {
                      "amount": 502,
                      "currency": "USD"
                    },
                    "quantity": 2,
                    "splitOption": "NONE",
                    "tickets": [
                      {
                        "row": "4",
                        "seat": "10",
                        "barcode": "VAY7-LLW793Q9"
                      },
                      {
                        "row": "4",
                        "seat": "11",
                        "barcode": "VAY7-KKH929Y2"
                      }
                    ]
                  }
                }
        
        response = self.send_req('/inventory/listings/v1/barcodes', token_type='USER',req_type = 'POST',params=params)
        print response
        print response.json()
         
    
    def update_barcodes(self, csv_name):
        
        barcode_csv_path = "barcode_csvs/%s.csv" %csv_name
        
        seat_10_codes = {}
        seat_11_codes = {}
        with open(barcode_csv_path,'rU') as barcode_file:
            reader = csv.reader(barcode_file)
            next(reader)
            
            for row in reader:
                stubhub_listing_id = row[1]
                seat_10_codes[stubhub_listing_id] = row[2]
                seat_11_codes[stubhub_listing_id] = row[3]
        
        row = 4
        for listing in seat_10_codes:
            print listing
            
            barcode_10 = seat_10_codes[listing]
            barcode_11 = seat_11_codes[listing]
            
            seat_10_dict = { "seat": "10","row": "4" ,"barcode": "%s" %barcode_10 }
            seat_11_dict = { "seat": "11","row": "4" ,"barcode": "%s" %barcode_11  }
                    
            params = { "listing": {"tickets": [seat_10_dict, seat_11_dict]} } 

            print "Listing: %s, %s" %(listing, params)
            response = self.send_req('/inventory/listings/v1/%s/barcodes' %(listing), token_type = 'USER', req_type='POST', params=params)
            #pdb.set_trace()
            #print response.header
            print response
            print response.text
            
        return None
    
    def update_barcodes_v2(self,csv_name):
        
        barcode_csv_path = "barcode_csvs/%s.csv" %csv_name
        
        seat_10_codes = {}
        seat_11_codes = {}
        
        with open(barcode_csv_path,'rU') as barcode_file:
            reader = csv.reader(barcode_file)
            next(reader)
            
            for row in reader:

                if row[1] != "":
                    stubhub_listing_id = "%s" %row[1].strip()
                  #  print stubhub_listing_id
                    seat_10_codes[stubhub_listing_id] = "%s" %row[2].upper().strip()
                    seat_11_codes[stubhub_listing_id] = "%s" %row[3].upper().strip()
        
        #pdb.set_trace()
        #print len(seat_10_codes)
        #print len(seat_11_codes)
        row = 4
        counter = 1
        error_codes = {}
        error_response = {}
        for listing in seat_10_codes:
            #print listing
            
            barcode_10 = seat_10_codes[listing]
            barcode_11 = seat_11_codes[listing]
            
         #   seat_10_dict = { "seat": "10","row": "4" ,"barcode": "%s" %barcode_10 }
          #  seat_11_dict = { "seat": "11","row": "4" ,"barcode": "%s" %barcode_11  }
                    
            params = { "products": [
                                {"row" : "4", "seat":"10", "fulfillmentArtifact" : "%s" %barcode_10, "operation" : "UPDATE"},
                                 {"row" : "4", "seat":"11", "fulfillmentArtifact" : "%s" %barcode_11, "operation" : "UPDATE"}  
                                   
                                   ] } 
            
            #pdb.set_trace()
            #print "Listing: %s, %s" %(listing, params)

            if counter <10:
               # pdb.set_trace()
                print "Listing: %s, %s" %(listing, params)
                response = self.send_req('/inventory/listings/v2/%s' %(listing), token_type = 'USER', req_type='PUT', params=params)
                
                print response.headers

                print response
                print response.text
                pdb.set_trace()
                if response !=200:
                    error_codes[listing] = response
                    error_response[listing] = response.text
                counter+=1
            else:
                 time.sleep(61)
                 counter=1
            
        print error_codes
        print error_response
    
    
    def get_all_listings(self):
        
        return self.send_req('/accountmanagement/listings/v1/seller/%s' %self.user_id, token_type='USER', req_type='GET' ).json()
        
    def relist_listing(self, listing_id):
                       
        return None        
                
#     def get_event_data(self, event_id, new_listings = None):
#         # Get XML of event details
#         event_details = self.get_event(event_id=event_id).text
#         #import pdb; pdb.set_trace()
#         #print event_details
#         #root = ET.fromstring(event_details)
#         event_details = event_details.encode('utf-8', 'ignore')
#         event_details = event_details.decode('ascii', 'ignore')
#         root = ET.fromstring(unicode(event_details.encode('utf-8')))
#         #print root[7].text
#         event_date_UTC_unformatted = root[7].text
#         event_date_UTC = dparser.parse(event_date_UTC_unformatted,fuzzy=True)
#         #event_date_UTC = datetime.datetime.strptime(event_date_UTC_unformatted[:16] , '%y-%M-%d:%H:%M')
#         #print event_date_UTC
#         #current_time = datetime.datetime.now(datetime.timezone.utc)
#        
#         for elem in root.iter(tag='secondaryName'):
#             opponent = elem.text
#         
#         now = datetime.datetime.utcnow().replace(tzinfo=utc)
#    
#         #current_time = datetime.datetime.utcnow()
#         # Calculate difference between now and event, in minutes
#         time_difference_in_days = event_date_UTC - now
#       
#         current_time_formatted = now.strftime("%Y-%m-%d %H:%M:%S")
#         event_date_formatted = event_date_UTC.strftime("%Y-%m-%d %H:%M:%S")
#         metadata = {'event_date':event_date_formatted, 'event_id' : event_id, 'time_difference' : time_difference_in_days, 'current_time':current_time_formatted}
#         
#         if new_listings !=None:
#             data = new_listings
#             sections_dict = {section['sectionId'] : section for section in data['section_stats']} 
#             zones_dict = {zone['zoneId'] : zone for zone in data['zone_stats']}
#             listings = data['listing']
#             total_tickets = data['totalTickets']
#             average_price = data['pricingSummary']['averageTicketPrice']
#             total_listings = data['totalListings']
#             
#             # Get team info
#             wins, losses, l_10 = espn.get_team_performance(event_id)
#     
#             return zones_dict, sections_dict, listings, metadata, event_id, total_tickets, average_price, wins, losses, l_10, opponent, total_listings
#         
#         else:
#             return metadata
#         
    def get_cheapest(self, eventId, section):
            
        listings = self.get_event_inventory(eventId)
        
        for listing in listings['section_stats']:
            if str(listing['sectionName'][-3:]) == str(section):  
                buyer_price_min = listing['minTicketPrice']

        return buyer_price_min
    
if __name__ == '__main__':
    
    username = USERNAME
    password = PASSWORD
    basic_auth = BASIC_AUTH
    app_token = APP_TOKEN
    
    try:
        app_token = Stubhub.get_app_token(app_token=app_token)
        user_token = Stubhub.get_user_token(basic_auth=basic_auth, username=username, password=password)
        user_id = Stubhub.get_user_id(basic_auth=basic_auth, username=username, password=password)
       # print user_token
        stubhub = Stubhub(app_token=app_token, user_token=user_token, user_id=user_id)
       # print stubhub.user_id
      #  print stubhub.user_token
        #x= stubhub.get_sales()
      #  print x
       # ids_dates, ids_opponents = stubhub.get_team_games('New York Mets')
      #  print ids_dates
       # print stubhub.get_event_inventory(9445062)

       # print stubhub.get_other_listing(1196917513)
        
       # print x['eventId']
        #stubhub.get_listings()
        #listing = 1187578939
        #print stubhub.change_price(listing, "500")
        #stubhub.create_listing_with_barcodes()
        #print stubhub.update_barcodes("feldo_mets")
        #stubhub.create_listing()
        #stubhub.update_barcodes_v2("feldo_fred_mets")
        #stubhub.change_price(1189209678, '415')
        
    except Exception as e:
        logging.error(traceback.format_exc())