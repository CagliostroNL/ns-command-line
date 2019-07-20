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

class NS:
    #Zet naam van stad om naar stad code
    def getStationCode(self, stName):
        url = 'https://gateway.apiportal.ns.nl/public-reisinformatie/api/v2/stations'
        self.header = {'Ocp-Apim-Subscription-Key': 'API-KEY'}
        req = requests.get(url, headers=self.header)
        getj = json.loads(req.text)
        jBase1 = getj['payload']
        for  i in range(len(jBase1)):
            station_lang = jBase1[i]['namen']['lang']
            if station_lang  == stName:
                station_code = jBase1[i]['code']
                return station_code
             
    def getTrip(self, van, naar, tijd=False, datum=False):
        def format_warning(text):
            return f'{bcolors.WARNING}{text}{bcolors.ENDC}'
        def print_warning(text):
            print(format_warning(text))

        url = f'https://gateway.apiportal.ns.nl/public-reisinformatie/api/v3/trips?fromStation={van}&toStation={naar}'

        if tijd is not False:
            url = f'https://gateway.apiportal.ns.nl/public-reisinformatie/api/v3/trips?fromStation={van}&toStation={naar}&dateTime={datum}T{tijd}'
       
        req = requests.get(url, headers=self.header)
        getj = json.loads(req.text)

        try:
            self.jBase = getj['trips']
        except KeyError:
            print_warning("Error! Mogelijk stationsnaam verkeerd getypt of het bestaat niet!")
            sys.exit()

        for i in range(len(self.jBase)):
                tTijd = self.jBase[i]['plannedDurationInMinutes']
                overstap = self.jBase[i]['transfers']
                vTijd = self.jBase[i]['legs'][0]['origin']['plannedDateTime']
                strp_time = datetime.datetime.strptime(vTijd, '%Y-%m-%dT%H:%M:%S%z') 
                strf_time = datetime.datetime.strftime(strp_time, '%Y-%m-%d %H:%M:%S') # RFC3339 naar beter leesbare tijd.
                spoor = self.jBase[i]['legs'][0]['origin']['plannedTrack']
                status = self.jBase[i]['status']

                if status == 'CANCELLED':
                   print_warning('Er is een rit geannuleerd in deze reis. Kijk op www.ns.nl voor meer informatie.')
                elif status == 'DISRUPTION':
                    print_warning('Mogelijk vertraging in deze rit. Kijk op www.ns.nl voor meer informatie.')
                elif status == 'ALTERNATIVE_TRANSPORT':
                    print_warning("Vervangend veroer in deze rit. Kijk op www.ns.nl voor meer informatie.")
                print(f"Duur van reis: {bcolors.OKBLUE}{tTijd}{bcolors.ENDC} minuten, aantal overstappen: {bcolors.OKBLUE}{overstap}{bcolors.ENDC},\
 vertrektijd: {bcolors.OKBLUE}{strf_time}{bcolors.ENDC}, spoor: {bcolors.OKBLUE}{spoor}{bcolors.ENDC}")
                leg = self.jBase[i]['legs']
                for x in range(len(leg)):
                    cancelled = leg[x]['cancelled']
                    richting = leg[x]['direction']
                    try:
                        spoor = leg[x]['origin']['plannedTrack'] 
                    except KeyError:
                        spoor = print_warning("Geen spoor gevonden. Mogelijk vervangend veroer of er is nog geen spoor bekend!")

                    uitstap = leg[x]['destination']['name']
                    print(f'Richting: {richting}, spoor:{bcolors.OKBLUE} {spoor}{bcolors.ENDC}, uitstappen: {uitstap}.')
                    if cancelled == True:
                        print_warning("Deze rit is geannuleerd!!")
                print('\n')
                    
def main():
    traintrip  = NS()

    parser = argparse.ArgumentParser(description='''NS Command line tool''')
    parser.add_argument("-v", "--van", type=str, required=True,  metavar='' ) 
    parser.add_argument("-n", "--naar", type=str, required=True,  metavar='')
    parser.add_argument("-d", "--datum", required=False, help="datum in jaar-maand-dag formaat",  metavar='' )
    parser.add_argument("-t", "--tijd",  required=False, help="tijd in uur:minuut, 24 uurs formaat", metavar='')

    args = parser.parse_args()

    traintrip.getStationCode(args.van)
    traintrip.getStationCode(args.naar)
    traintrip.getTrip(args.van, args.naar, args.tijd, args.datum)

if __name__ =='__main__':
    main()
