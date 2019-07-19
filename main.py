#!/usr/bin/python3

import sys
import requests
import json
import argparse
import datetime 

class bcolors:
    OKBLUE = '\033[94m'
    WARNING = '\033[31m'
    ENDC = '\033[0m'

class ns:
    #Zet naam van stad om naar stad code
    def getStationCode(self, stName):
        url = 'https://gateway.apiportal.ns.nl/public-reisinformatie/api/v2/stations'
        self.header = {'Ocp-Apim-Subscription-Key': 'NS-API-KEY-HIER'}
        req = requests.get(url, headers=self.header)
        getj = json.loads(req.text)
        jBase1 = getj['payload']
        stName.lower()
        
        for  i in range(len(jBase1)):
            nou = jBase1[i]['namen']['lang']
            nou.lower()
            if nou  == stName:
                stCode = jBase1[i]['code']

                return stCode
             
    def getTrip(self, van, naar, tijd=False, datum=False):
        url = f'https://gateway.apiportal.ns.nl/public-reisinformatie/api/v3/trips?fromStation={van}&toStation={naar}'
        if tijd is not False:
            url = f'https://gateway.apiportal.ns.nl/public-reisinformatie/api/v3/trips?fromStation={van}&toStation={naar}&dateTime={datum}T{tijd}'
        req = requests.get(url, headers=self.header)
        getj = json.loads(req.text)
        try:
            self.jBase = getj['trips']
        except KeyError:
            print(f"{bcolors.WARNING}.Error! Mogelijk stationsnaam verkeerd getypt of het bestaat niet!{bcolors.ENDC}")
            sys.exit()
        for i in range(len(self.jBase)):
                tTijd = self.jBase[i]['plannedDurationInMinutes']
                overS = self.jBase[i]['transfers']
                vTijd = self.jBase[i]['legs'][0]['origin']['plannedDateTime']
                strp_time = datetime.datetime.strptime(vTijd, '%Y-%m-%dT%H:%M:%S%z') 
                strf_time = datetime.datetime.strftime(strp_time, '%Y-%m-%d %H:%M:%S') # RFC3339 naar beter leesbare tijd.
                spr = self.jBase[i]['legs'][0]['origin']['plannedTrack']
                status = self.jBase[i]['status']
                if status == 'CANCELLED':
                    print(f'{bcolors.WARNING}Er is een rit geannuleerd in deze reis. Kijk op www.ns.nl voor meer informatie.{bcolors.ENDC}')
                elif status == 'DISRUPTION':
                    print(f'{bcolors.WARNING}Mogelijk vertraging in deze rit. Kijk op www.ns.nl voor meer informatie.{bcolors.ENDC}')
                elif status == 'ALTERNATIVE_TRANSPORT':
                    print(f"{bcolors.WARNING}Vervangend veroer in deze rit. Kijk op www.ns.nl voor meer informatie.{bcolors.ENDC}")
                print(f"Duur van reis: {bcolors.OKBLUE}{tTijd}{bcolors.ENDC} minuten, aantal overstappen: {bcolors.OKBLUE}{overS}{bcolors.ENDC},\
 vertrektijd: {bcolors.OKBLUE}{strf_time}{bcolors.ENDC}, spoor: {bcolors.OKBLUE}{spr}{bcolors.ENDC}")
                leg = self.jBase[i]['legs']
                for x in range(len(leg)):
                    can = leg[x]['cancelled']
                    dis = leg[x]
                    richting = leg[x]['direction']
                    try:
                        spr = leg[x]['origin']['plannedTrack'] 
                    except KeyError:
                        spr = f"{bcolors.WARNING}Geen spoor gevonden. Mogelijk vervangend veroer of er is nog geen spoor bekend!{bcolors.ENDC}"

                    uitstap = leg[x]['destination']['name']
                    print(f'Richting: {richting}, spoor:{bcolors.OKBLUE} {spr}{bcolors.ENDC}, uitstappen: {uitstap}.')
                    if can == True:
                        print(f'{bcolors.WARNING}Deze rit is geannuleerd!!{bcolors.ENDC}')
                print('\n')
                    

NS  = ns()

parser = argparse.ArgumentParser(description='''NS Command line tool''')
parser.add_argument("-v", "--van", type=str, required=True,  metavar='' ) 
parser.add_argument("-n", "--naar", type=str, required=True,  metavar='')
parser.add_argument("-d", "--datum", required=False, help="datum in jaar-maand-dag formaat",  metavar='' )
parser.add_argument("-t", "--tijd",  required=False, help="tijd in uur:minuut, 24 uurs formaat", metavar='')

args = parser.parse_args()

NS.getStationCode(args.van)
NS.getStationCode(args.naar)
NS.getTrip(args.van, args.naar, args.tijd, args.datum)
