from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
import idna
import json
from socket import socket
from collections import namedtuple
from datetime import datetime
import pprint

HostInfo = namedtuple(field_names='cert hostname peername', typename='HostInfo')


def get_certificate(hostname, port):
    hostname_idna = idna.encode(hostname)
    sock = socket()

    sock.connect((hostname, port))
    peername = sock.getpeername()
    ctx = SSL.Context(SSL.SSLv23_METHOD) # most compatible
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    crypto_cert = cert.to_cryptography()
    sock_ssl.close()
    sock.close()

    return HostInfo(cert=crypto_cert, peername=peername, hostname=hostname)

def  get_alt_names(cert):
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return None

def get_common_name(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None

def get_issuer(cert):
    try:
        names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        #cmp = cert.issuer.get_components()
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def get_json_result(hostinfo):
    common_name = get_common_name(hostinfo.cert)
    san =get_alt_names(hostinfo.cert),
    issuer = get_issuer(hostinfo.cert)

    now  = datetime.now()
    delta = hostinfo.cert.not_valid_after - now   
    days_to_expiration = delta.days
    is_expired = days_to_expiration < 0 
    is_self_signed = common_name == issuer
    date_time = hostinfo.cert.not_valid_before.strftime("%m/%d/%Y")

    cert_details = {
        'hostname': hostinfo.hostname,
        'ip': hostinfo.peername[0],
        'commonName':common_name,
        'is_self_signed':is_self_signed,
        'SAN': san,
        'is_expired': is_expired,
        'issuer': issuer,
        'not_valid_before': hostinfo.cert.not_valid_before.strftime("%m/%d/%Y"),
        'not_valid_after': hostinfo.cert.not_valid_after.strftime("%m/%d/%Y"),
        'days_to_expiration': days_to_expiration
    }

    return cert_details
    
@output_handler
def main():
    siemplify = SiemplifyAction()

    url = siemplify.extract_action_param("Url to check", print_value=True)
    hostinfo = get_certificate(url, 443)
    json_res = get_json_result(hostinfo)
    output_message = "Url Certificate <{0}> was successfully analyzed.".format(url)
    pprint.pprint(json_res)
    print(json_res)
    siemplify.result.add_result_json(json_res)

    siemplify.end(output_message, True, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
