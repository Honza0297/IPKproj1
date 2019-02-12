import argparse
import socket
import re

import xml.etree.ElementTree as XML
from lxml import etree

# Default values defined here:

port_num = 80
host_name = "api.openweathermap.org"
example_data = "GET /data/2.5/weather?q=Brno&units=metric&mode=xml&appid=5e565f7756eebd498b0df0b91471a3b7 HTTP/1.1\r\n"

# regexes are defined here:



def get_args():
    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()

    # Kvuli nekompatibilnimu zadavani argumentu s argparse nutno odstranit prefixy "name=" - nova fce?
    if args.api_key.startswith("api_key=") and args.city.startswith("city="):
        args.api_key = args.api_key[len("api_key="):]
        args.city = args.city[len("city="):]
    else:
        raise Exception("Bad structure of input args. Type --help for help")

    return args


def add_args(parser):
    parser.add_argument(dest="api_key", help="api_key")
    parser.add_argument(dest="city", help="Specifies in which city you want to display weather")

def print_result(values):
    """
    Function prints the values extracted from response in given format.
    :param values: dict-like structure, proper keys you can see below
    :return: nothing
    """
    print("City: ", values["city"]["name"])
    print("Clouds: ", values["clouds"]["name"])
    print("Temperature: ", values["temperature"]["value"], "degrees Celsius")
    print("Humidity: ", values["humidity"]["value"],"%")
    print("Pressure: ", values["pressure"]["value"], "hPa")
    print("Wind speed: ", values["speed"]["value"])
    print("Wind degree: ", values["direction"]["value"])

args = get_args()


# Here becomes the FUN :)

# Prepare socket and send request
api_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
api_socket.connect((host_name, port_num))
api_socket.send(b"GET /data/2.5/weather?q=Ushuaia&units=metric&mode=xml&appid=5e565f7756eebd498b0df0b91471a3b7 HTTP/1.1\r\nHost: www.api.openweathermap.org\r\n\r\n\n\r\n")

# Get response and cast it to string
response = str(api_socket.recv(4096))
xml_data = re.search("(\<\?xml.*)", response).group(1)
xml_data = xml_data.replace("\\n", "")
xml_data = xml_data+" "
#print(xml_data)

# Parse that f... file O:) into XML

parser = etree.XMLParser(recover=True)
pokus = XML.ElementTree(XML.fromstring(xml_data,parser=parser))

#print(type(pokus))
dict_for_print = dict()



for node in pokus.iter():
    #print(node.tag, node.attrib)
    dict_for_print[node.tag] = node.attrib or None
print_result(dict_for_print)
exit()

"""
dict_for_print = dict()
dict_for_print["city"] = args.city
dict_for_print["clouds"] = re.search("", xml_data).group(1) or None
dict_for_print["temperature"] = None
dict_for_print["humidity"] = None
dict_for_print["pressure"] = None
dict_for_print["wind"] = None
dict_for_print["direction"] = None
"""
print_result(dict_for_print)
