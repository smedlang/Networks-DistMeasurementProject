#Savita Medlang
#GeoDistance.py
#Calculate the distance between the local computer and target hostnames

import json
import requests
from socket import gethostbyname
from math import *

def main():
    # Get the location of the current computer.
    my_loc = locate()

    if my_loc[0] == None and my_loc[1] == None:
        raise Exception("Your location could not be found.")

    input_file = open("targets.txt")

    output_result = "Self:\nLatitude: {}\nLongitude: {}\n".format(my_loc[0], my_loc[1])
    print (output_result)

    target_hosts = input_file.read().splitlines()

    # Iterate through each target host to loacte their location.
    for host in target_hosts:
        # Locate the host's loaction by their name.
        host_location = locate_host(gethostbyname(host))

        shortest_distance = None
        if host_location[0] != None and host_location[1] != None:
            # Get the shortest distance between this computer's IP and the host's IP.
            shortest_distance = calculate_distance(my_loc, host_location)
        else:
            raise Exception("Host location could not be found.")

        output_result = "Host: {}\nIP address: {}\nDistance: {} km\n".format(host, gethostbyname(host), shortest_distance)
        print ("Latitude: {}\nLongitude: {}".format(host_location[0], host_location[1]))
        print (output_result)

    input_file.close()

# Locate the Latitude and Longitude of the given IP address.
def locate_host(IP_address):
    # using website freegeoip to get the location of the targets
    response = requests.get('http://freegeoip.net/json/{}'.format(IP_address))
    info = json.loads(response.text)

    latitude = None
    longitude = None

    latitude = info['latitude']
    longitude = info['longitude']

    return latitude, longitude

def locate():
    # gets ip address of local computer using ip.42.pl
    request = requests.get('http://ip.42.pl/raw')
    myIP = request.text

    my_loc = locate_host(myIP)

    return my_loc

#Used the haversine formula to calculate the distance 
def calculate_distance(start_coordinate, end_coordinate):
    # convert to radians
    start_lat, start_long, end_lat, end_long = map(radians, [start_coordinate[0], start_coordinate[1], end_coordinate[0], end_coordinate[1]])

    # lat and long space:
    # the difference between the two coordinates 
    lat_distance = end_lat - start_lat
    long_distance = end_long - start_long

    # haversine formula below here
    a = sin(lat_distance/2) * sin(lat_distance/2) + cos(start_lat) * cos(end_lat) * sin(long_distance/2) * sin(long_distance/2)
    c = 2 * asin(sqrt(a))

    # Convert to km.
    shortest_distance = c * 6367

    return shortest_distance

if __name__ == "__main__":
    main()
