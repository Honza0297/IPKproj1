import argparse
import socket
import re
import xml.etree.ElementTree as XML
import sys  # Only for sys.stderr

# Default values defined here, default city and default_api_key for run without params:
# default_city = "Brno"
# default_api_key = "5e565f7756eebd498b0df0b91471a3b7"
port_num = 80
host_name = "api.openweathermap.org"
broadcast_data = "GET /data/2.5/weather?q={0}&units=metric&mode=xml&appid={1} HTTP/1.1\r\nHost: {2}\r\n\r\n"

# regexes are defined here:
# old regex for xml preparation from response: "(<\?xml.*(?<!'))"
xml_regex = re.compile("(<\?xml.*\n.*)")
code_regex = re.compile("([0-9]{3})")


def get_args():
    """
    Function gets args via argparse module.
    :return: argparse tuple with arguments
    """
    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()
    if not(args.api_key and args.city):
        print("Arguments were not given properly.", file=sys.stderr)
        exit(1)

    return args


def add_args(parser):
    """
    Function adds arguments to argparse parser.
    :param parser: Argparse parser
    :return: None
    """
    parser.add_argument("--api_key", dest="api_key", help="api_key")
    parser.add_argument("--city", dest="city", help="Specifies in which city you want to display weather")


def print_result(values):
    """
    Function prints the values extracted from response in given format.
    :param values: dict-like structure, proper keys you can see below
    :return: None
    """
    print("City: ", values["city"]["name"])
    print("Clouds: ", values["clouds"]["name"])
    print("Temperature: ", values["temperature"]["value"], "°C")
    print("Humidity: ", values["humidity"]["value"], "%")
    print("Pressure: ", values["pressure"]["value"], "hPa")
    print("Wind speed: ", values["speed"]["value"], "km/h")
    print("Wind degree: ", values["direction"]["value"], "degrees")


def prepare_socket():
    """
    Function prepares socket and connect to host.
    :return: None
    """
    ret_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ret_socket.connect((host_name, port_num))
    except Exception as err:
        print("The connection failed. Details: \n", err.__repr__(), file=sys.stderr)
        exit(1)

    return ret_socket


def send_and_get_msg(sock: socket, values):
    """
    Function handles communication between client and server and returns it.
    :param sock: socket for comm
    :param values: values to specify city and api_key used in communication
    :return: server response
    """
    ret = None
    try:
        sock.send(bytes(broadcast_data.format(values.city,
                                              values.api_key,
                                              host_name), "utf-8"))
    except Exception as err:
        print("Failed to send a request. Details:\n", err.__repr__(), file=sys.stderr)
        exit(1)

    try:
        ret = str(sock.recv(2048), "utf-8")
    except Exception as err:
        print("An exception during receiving a response has occurred. Details: \n", err.__repr__(), file=sys.stderr)
        exit(1)
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
    xml_tree = None
    try:
        xml_tree = XML.fromstring(xml_part)
    except Exception as err:
        print("An Exception has occurred during XML conversion. Details: \n", err.__repr__(), file=sys.stderr)
        exit(1)

    return xml_tree


def check_err(resp):
    """
    Function checks the response for problems
    :param resp: response of the server. Can be None
    :return: Code of
    """
    resp_ret_code = re.search(code_regex, resp).group(1)
    if int(resp_ret_code) == 200:

        return 0
    else:
        return resp_ret_code


# Main body starts here
args = get_args()
api_socket = prepare_socket()
response = send_and_get_msg(api_socket, args)
api_socket.close()
err_code = check_err(response)
if err_code:
    print("HTTP response error occurred. Fail code: ", err_code, file=sys.stderr)
    exit(1)

xml_data = parse_to_xml(response)
dict_for_print = {node.tag: node.attrib for node in xml_data.iter()}  # XML tree to dict
print_result(dict_for_print)  # And finally print the result :)
