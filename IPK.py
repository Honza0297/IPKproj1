import argparse
import socket
import re
import xml.etree.ElementTree as XML
from lxml import etree

# Default values defined here:
default_city = "Brno"
default_api_key = "5e565f7756eebd498b0df0b91471a3b7"
port_num = 80
host_name = "api.openweathermap.org"
broadcast_data = "GET /data/2.5/weather?q={0}&units=metric&mode=xml&appid={1} HTTP/1.1\r\nHost: {2}\r\n\r\n"

# regex is defined here:
xml_regex = re.compile('(<\?xml.*)')


def get_args():
    """
    Function gets args via argparse module.
    :return: argparse tuple with arguments
    """
    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()

    # Because of some incompatibility between argparse and task, need to delete prefixes like "city="
    # BTW: Right way in argparse is "--city="
    if args.api_key.startswith("api_key=") and args.city.startswith("city="):
        args.api_key = args.api_key[len("api_key="):]
        args.city = args.city[len("city="):]
    else:
        raise Exception("Bad structure of input args. Type --help for help")

    return args


def add_args(parser):
    """
    Function adds arguments to argparse parser.
    :param parser: Argparse parser
    :return: None
    """
    parser.add_argument(dest="api_key", help="api_key")
    parser.add_argument(dest="city", help="Specifies in which city you want to display weather")


def print_result(values):
    """
    Function prints the values extracted from response in given format.
    :param values: dict-like structure, proper keys you can see below
    :return: None
    """
    print("City: ", values["city"]["name"])
    print("Clouds: ", values["clouds"]["name"])
    print("Temperature: ", values["temperature"]["value"], "degrees Celsius")
    print("Humidity: ", values["humidity"]["value"],"%")
    print("Pressure: ", values["pressure"]["value"], "hPa")
    print("Wind speed: ", values["speed"]["value"])
    print("Wind degree: ", values["direction"]["value"])


def prepare_socket():
    """
    function prepares socket and connect to host.
    :return: None
    """
    ret_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ret_socket.connect((host_name, port_num))
    return ret_socket


def send_and_get_msg(sock: socket, values):
    """
    Function handles communication between client and server and returns it.
    :param sock: socket for comm
    :param values: values to specify city and api_key used in communication
    :return: server response
    """
    sock.send(bytes(broadcast_data.format(values.city or default_city,
                                          values.api_key or default_api_key,
                                          host_name), "utf-8"))
    ret = str(sock.recv(2048))
    return ret


def parse_to_xml(resp: str):
    """
    Function parses server response to a XML
    :param resp: server response
    :return: XML tree
    """
    xml_part = xml_regex.search(resp).group(1)
    xml_part = xml_part.replace("\\n", "\n")  # EOL is "\\n" instead of newline char "\n", so need to fix it

    # Parse that to XML tree
    parser = etree.XMLParser(recover=True)
    xml_tree = XML.ElementTree(XML.fromstring(xml_part, parser=parser))
    return xml_tree


# Main body starts here
args = get_args()
api_socket = prepare_socket()
response = send_and_get_msg(api_socket, args)
xml_data = parse_to_xml(response)
dict_for_print = {node.tag: node.attrib for node in xml_data.iter()}  # XML tree to dict
print_result(dict_for_print)  # And finally print the result :)
