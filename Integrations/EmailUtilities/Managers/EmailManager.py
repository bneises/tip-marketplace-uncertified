import olefile
import OleId
from msg_parser import MsOxMessage
import extract_msg
import typing
import hashlib
import re
from tld import get_tld, get_fld
import ipaddress
import magic
from email.utils import parseaddr, getaddresses
from collections import Counter
from urlextract import URLExtract
import email.errors
import email.header
import chardet
import EmailParserRouting
import datetime
import dateutil.parser
import json
from json import JSONEncoder
from html import unescape
import uuid
import os
import base64
import urllib
import time
from SiemplifyUtils import dict_to_flat
import ioc_fanger
from SiemplifyDataModel import EntityTypes
from io import BytesIO
from html2text import HTML2Text
import string
from urllib.parse import unquote, urlparse, parse_qs


''' Regexes used by the parser '''
IPV4_REGEX = re.compile(r'''(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})''')
IPV6_REGEX = re.compile(r'''((?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)''')
WINDOW_SLICE_REGEX = re.compile(r'''\s''')
EMAIL_REGEX = re.compile(r'''([a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*)''', re.MULTILINE)
EMAIL_TLD_REGEX = re.compile(r'''([a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)''', re.MULTILINE)
recv_dom_regex = re.compile(r'''(?:(?:from|by)\s+)([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]{2,})+)''', re.MULTILINE)

IOC_TYPES = {"urls": "DestinationURL", "emails": "USERUNIQNAME", "ips": "ADDRESS", "domains": "DOMAIN", "hashes": "FILEHASH"}

def compile_re(string):
    return re.compile(string, flags=re.IGNORECASE|re.MULTILINE)
    
ENTITY_REGEXS = {
        "FILEHASH":{
            "patterns":[
                    compile_re(r'''(?:(?<=\s)|(?<=^))([a-f0-9]{32})(?:(<=\s)|(?<=$)|(?<=\b))''')
                ,
                    compile_re(r'''(?:(?<=\s)|(?<=^))([a-f0-9]{64})(?:(<=\s)|(?<=$)|(?<=\b))''')
                ,
                    compile_re(r'''(?:(?<=\s)|(?<=^))([a-f0-9]{128})(?:(<=\s)|(?<=$)|(?<=\b))''')
                ,
                    compile_re(r'''(?:(?<=\s)|(?<=^))([a-f0-9]{40})(?:(<=\s)|(?<=$)|(?<=\b))''')
                
            ]
        },
        "DestinationURL":{
            "patterns":[
                    #compile_re(r'''(?i)\b(?:(?:https?|ftps?|http?):(?:/{1,3}|[a-z0-9%])(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:[\w\-._~%!$&'()*+,;=:/?#\[\]@]+)|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:\w)\b/?(?!@)))''')
                    compile_re(r'''(?i)\b(?:(?:https?|ftps?|http?){1}:(?:\/{2}|[a-z0-9%])(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:[\w\-._~%!$&'()*+,;=:\/?#\[\]@]+))''')
            ]
        },
        "ADDRESS":{
            "patterns": [
                    compile_re(r'''(?:(?:1\d\d|2[0-5][0-5]|2[0-4]\d|0?[1-9]\d|0?0?\d)\.|.*?\[\.\]|\.|\.){3}(?:1\d\d|2[0-5][0-5]|2[0-4]\d|0?[1-9]\d|0?0?\d)''')
            ]
        }
    }



EXTEND_GRAPH_URL = '{}/external/v1/investigator/ExtendCaseGraph'

class EmailEncoder(JSONEncoder):
    def default(self,o):
        return o.__dict__
        
maketrans = str.maketrans

class URLDefenseDecoder(object):

    @staticmethod
    def __init__():
        URLDefenseDecoder.ud_pattern = re.compile(r'https://urldefense(?:\.proofpoint)?\.com/(v[0-9])/')
        URLDefenseDecoder.v1_pattern = re.compile(r'u=(?P<url>.+?)&k=')
        URLDefenseDecoder.v2_pattern = re.compile(r'u=(?P<url>.+?)&[dc]=')
        #URLDefenseDecoder.v3_pattern = re.compile(r'v3/__(?P<url>.+?)__;(?P<enc_bytes>.*?)!')
        URLDefenseDecoder.v3_pattern = re.compile(r'v3/__(?P<url>.+?)__(;(?P<enc_bytes>.*?)!)?')
        URLDefenseDecoder.v3_token_pattern = re.compile(r"\*(\*.)?")
        URLDefenseDecoder.v3_single_slash = re.compile(r"^([a-z0-9+.-]+:/)([^/].+)", re.IGNORECASE)
        URLDefenseDecoder.v3_run_mapping = {}
        run_values = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-' + '_'
        run_length = 2
        for value in run_values:
            URLDefenseDecoder.v3_run_mapping[value] = run_length
            run_length += 1

    def decode(self, rewritten_url):
        match = self.ud_pattern.search(rewritten_url)
        if match:
            if match.group(1) == 'v1':
                return self.decode_v1(rewritten_url)
            elif match.group(1) == 'v2':
                return self.decode_v2(rewritten_url)
            elif match.group(1) == 'v3':
                return self.decode_v3(rewritten_url)
            else:
                raise ValueError('Unrecognized version in: ', rewritten_url)
        else:
            return rewritten_url

    def decode_v1(self, rewritten_url):
        match = self.v1_pattern.search(rewritten_url)
        if match:
            url_encoded_url = match.group('url')
            html_encoded_url = unquote(url_encoded_url)
            url = unescape(html_encoded_url)
            return url
        else:
            raise ValueError('Error parsing URL')

    def decode_v2(self, rewritten_url):
        match = self.v2_pattern.search(rewritten_url)
        if match:
            special_encoded_url = match.group('url')
            trans = maketrans('-_', '%/')
            url_encoded_url = special_encoded_url.translate(trans)
            html_encoded_url = unquote(url_encoded_url)
            url = unescape(html_encoded_url)
            return url
        else:
            raise ValueError('Error parsing URL')

    def decode_v3(self, rewritten_url):
        def replace_token(token):
            if token == '*':
                character = self.dec_bytes[self.current_marker]
                self.current_marker += 1
                return character
            if token.startswith('**'):
                run_length = self.v3_run_mapping[token[-1]]
                run = self.dec_bytes[self.current_marker:self.current_marker + run_length]
                self.current_marker += run_length
                return run

        def substitute_tokens(text, start_pos=0):
            match = self.v3_token_pattern.search(text, start_pos)
            if match:
                start = text[start_pos:match.start()]
                built_string = start
                token = text[match.start():match.end()]
                built_string += replace_token(token)
                built_string += substitute_tokens(text, match.end())
                return built_string
            else:
                return text[start_pos:len(text)]

        match = self.v3_pattern.search(rewritten_url)
        if match:
            url = match.group('url')
            singleSlash = self.v3_single_slash.findall(url)
            if singleSlash and len(singleSlash[0]) == 2:
                url = singleSlash[0][0] + "/" + singleSlash[0][1]
            encoded_url = unquote(url)
            if match.group('enc_bytes'):
                enc_bytes = match.group('enc_bytes')
                enc_bytes += '=='
                self.dec_bytes = (urlsafe_b64decode(enc_bytes)).decode('utf-8')
                self.current_marker = 0
                return substitute_tokens(encoded_url)
            else:
                return encoded_url

        else:
            raise ValueError('Error parsing URL')
        
class EmailUtils(object):


    def __init__(self, custom_regex=None):
        self.custom_regex = custom_regex
        pass
    

        
    @staticmethod
    def attachment(filename, content):
        mime_type, mime_type_short = EmailUtils.get_mime_type(content)
        attachment_json = {
            'filename': filename,
            'size': len(content),
            'extension': os.path.splitext(filename)[1][1:],
            'hash': {
                'md5': hashlib.md5(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
                'sha256': hashlib.sha256(content).hexdigest(),
                'sha512': hashlib.sha512(content).hexdigest()
            },
            'mime_type': mime_type,
            'mime_type_short': mime_type_short,
            'raw': base64.b64encode(content).decode()
        }
        return attachment_json      
        
    @staticmethod
    def clean_found_url(url):
        
        if '.' not in url and '[' not in url:
            # if we found a URL like e.g. http://afafasasfasfas; that makes no
            # sense, thus skip it. Include http://[2001:db8::1]
            return

        try:
            url = url.lstrip('"\'\t \r\n').replace('\r', '').replace('\n', '').rstrip('/')
            url = urllib.parse.urlparse(url).geturl()
            
            if ':/' in url[:10]:
                scheme_url = re.sub(r':/{1,3}', '://', url, count=1)
            else:
                scheme_url = 'noscheme://' + url
            tld = urllib.parse.urlparse(scheme_url).hostname.rstrip('.').rsplit('.', 1)[-1].lower()
            if tld in ('aspx', 'css', 'gif', 'htm', 'html', 'js', 'jpg', 'jpeg', 'php', 'png',):
                #print('returning clean with no url')
                return
        except ValueError:
            #print('Unable to parse URL - %s', url)
            return

        # let's try to be smart by stripping of noisy bogus parts
        url = re.split(r'''[', ")}\\]''', url, 1)[0]

        # filter bogus URLs
        if url.endswith('://'):
            #print('returning clean with no url')
            return
        if '&' in url:
            url = unescape(url)
        #print(f'post clean: {url}')
        return url    
        
    @staticmethod
    def string2date(line):
        
        default_date = '1970-01-01T00:00:00+0000'

        # if the input is empty, we return a default date
        if line == '':
            return dateutil.parser.parse(default_date)

        try:
            date_ = email.utils.parsedate_to_datetime(line)
        except (TypeError, ValueError, LookupError):
            

            try:
                date_ = dateutil.parser.parse(line)
            except (AttributeError, ValueError, OverflowError):
                # Now we are facing an invalid date.
                return dateutil.parser.parse(default_date)

        if date_.tzname() is None:
            return date_.replace(tzinfo=datetime.timezone.utc)

        return date_    
    
    @staticmethod
    def get_file_hash(data):
        """Generate hashes of various types (``MD5``, ``SHA-1``, ``SHA-256``, ``SHA-512``)\
        for the provided data.

        Args:
          data (bytes): The data to calculate the hashes on.

        Returns:
          dict: Returns a dict with as key the hash-type and value the calculated hash.
        """
        hashalgo = ['md5', 'sha1', 'sha256', 'sha512']
        hash_ = {}

        for k in hashalgo:
            ha = getattr(hashlib, k)
            h = ha()
            h.update(data)
            hash_[k] = h.hexdigest()

        return hash_    
        
    @staticmethod
    def decode_string(string, encoding):
        if string == b'':
            return ''

        if encoding is not None:
            try:
                return string.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                pass

        if chardet:
            enc = chardet.detect(string)
            if not (enc['confidence'] is None or enc['encoding'] is None) and not (enc['confidence'] == 1 and enc['encoding'] == 'ascii'):
                value = string.decode(enc['encoding'], 'replace')
            else:
                value = string.decode('ascii', 'replace')
        else:
            text = ''

            for e in ('latin1', 'utf-8'):
                try:
                    text = string.decode(e)
                except UnicodeDecodeError:
                    pass
                else:
                    break

            if text == '':
                value = string.decode('ascii', 'ignore')
            else:
                value = text

        return value        
        
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code."""
        if isinstance(obj, datetime.datetime):
            if obj.tzinfo is not None:
                serial = obj.astimezone(datetime.timezone.utc).isoformat()
            else:
                serial = obj.isoformat()

            return serial

        raise TypeError('Type not serializable - {}'.format(str(type(obj))))


    def export_to_json(parsed_msg, sort_keys=False):
        """Function to convert a parsed e-mail dict to a JSON string.

        Args:
            parsed_msg (dict): The parsed e-mail dict which is the result of
                               one of the decode_email functions.
            sort_keys (bool, optional): If True, sorts the keys in the JSON output.
                                        Default: False.

        Returns:
            str: Returns the JSON string.
        """
        return json.dumps(parsed_msg, default=EmailUtils.json_serial, cls=EmailEncoder, sort_keys=sort_keys, indent=2)
        
    @staticmethod
    def decode_field(field):
        try:
            _decoded = email.header.decode_header(field)
        except email.errors.HeaderParseError:
            return field

        string = ''

        for _text, charset in _decoded:
            if charset:
                string += EmailUtils.decode_string(_text, charset)
            else:
                if isinstance(_text, bytes):
                    string += _text.decode('utf-8', 'ignore')
                else:
                    string += _text
        return string

    @staticmethod
    def get_mime_type(data):
        """Get mime-type information based on the provided bytes object.

        Args:
            data: Binary data.

        Returns:
            typing.Tuple[str, str]: Identified mime information and mime-type. If **magic** is not available, returns *None, None*.
                                    E.g. *"ELF 64-bit LSB shared object, x86-64, version 1 (SYSV)", "application/x-sharedlib"*
        """
        if magic is None:
            return None, None

        detected = magic.detect_from_content(data)
        return detected.name, detected.mime_type            
    
 
        
    @staticmethod
    def is_ole_file(content_bytes):
        try:
            return olefile.isOleFile(content_bytes)
        except (FileNotFoundError, ValueError):
            return False        
    
    @staticmethod
    def extract_ips(body, include_internal=False):
        ips: typing.Counter[str] = Counter()
        for ip_type in [IPV4_REGEX, IPV6_REGEX]:
            for match in ip_type.findall(body):
                try:
                    ipaddress_match = ipaddress.ip_address(match)
                except ValueError:
                    continue
                else:
                    
                    if not (ipaddress_match.is_private) or include_internal and match != '::':
                        ips[match] = 1
        return list(ips)               
        
    @staticmethod
    def extract_domains_from_urls(urls):
        # Extract domains
        domains: typing.Counter[str] = Counter()
        for match in urls: 
            try:
                dom = get_fld(match.lower(), fix_protocol=True)
                domains[dom] = 1
            except Exception as t:
                pass
        return list(domains)
        
    @staticmethod
    def extract_emails(body):
        extracted_emails = {}
        extractor = URLExtract(cache_dns=False, extract_email=True)
        
        for match in extractor.find_urls(body): # Loop over results and extract emails and remove mailto:
            c = URLExtract(cache_dns=False)
            removedurl = c.find_urls(match, check_dns=False)
            if not removedurl:
                #match = match.replace('mailto:', '')
                match = re.sub(r'^.*mailto:', '', match)
                match = re.sub(r'^.*:', '', match)
                emails = match.split(",")
                for e in emails:
                    extracted_emails[e.lower()] = 1
        return list(extracted_emails)        

    @staticmethod
    def get_urls(body: str) -> typing.List[str]:
        """Function for extracting URLs from the input string.
        Args:
            body (str): Text input which should be searched for URLs.
        Returns:
            list: Returns a list of URLs found in the input string.
        """
        list_observed_urls: typing.Counter[str] = Counter()
        extractor = URLExtract(cache_dns=False)
        for found_url in extractor.find_urls(body, check_dns=True):
            if '.' not in found_url:
                # if we found a URL like e.g. http://afafasasfasfas; that makes no
                # sense, thus skip it
                continue
            try:
                ipaddress_match = ipaddress.ip_address(found_url)
                # we want to skip any IP addresses we find in the body.  These will be
                # added when via the extract_ips method.
                continue
            except ValueError:
                pass
            clean_uri = EmailUtils.clean_found_url(found_url)
            if clean_uri is not None:
                list_observed_urls[clean_uri] = 1
        return list(list_observed_urls)

    def parsed_entities(self, in_str):
        
        entities = []
        entities.extend([])
        urls = EmailUtils.get_urls(in_str)
        for url in urls:
            entity = {}
            entity['entity_type'] = 'DestinationURL'
            entity['identifier'] = url
            entities.append(entity)
            
        
        for domain in EmailUtils.extract_domains_from_urls(urls):
            entity = {}
            entity['entity_type'] = 'DOMAIN'
            entity['identifier'] = domain
            entities.append(entity)

        for user in EmailUtils.extract_emails(in_str):
            entity = {}
            entity['entity_type'] = 'USERUNIQNAME'
            entity['identifier'] = user
            entities.append(entity)


        for ip in EmailUtils.extract_ips(in_str, include_internal=True):
            entity = {}
            entity['entity_type'] = 'ADDRESS'
            entity['identifier'] = ip
            entities.append(entity)    
        
        entities.extend(self.custom_entities(in_str))
        return entities        

    
    def custom_entities(self, in_str):
        matched_entities = []
        for entity_source in [ENTITY_REGEXS, self.custom_regex]:
            for entity_type in entity_source:
                for regex_search in entity_source[entity_type]['patterns']:
                    matches = re.finditer(regex_search, in_str)
                    if bool(matches):
                        for m in matches:
                            entity = {}
                            entity['entity_type'] = entity_type
                            if entity_type == 'DestinationURL':
                                entity['identifier'] = EmailUtils.clean_found_url(m.group(0))
                            else:
                                entity['identifier'] = m.group(0)
                            matched_entities.append(entity)
        return matched_entities
        
    @staticmethod
    def parse_routing(entries):
        r = {}
        r['hosts'] = []
        r['ips'] = []
        r['domains'] = []
        
        for entry in entries:
            try:
                ip_obj = ipaddress.ip_address(entry)
            except ValueError:
                try:
                    dom = get_fld(entry.lower(), fix_protocol=True)
                    r['domains'].append(dom)
                    r['hosts'].append(entry)
                except Exception as e:
                    r['hosts'].append(entry)
            else:
                if not (ip_obj.is_private):
                    r['ips'].append(str(ip_obj))
        return r
        
    @staticmethod
    def routing_entities(route):
        r = {}
        r['ips'] = []
        r['domains'] = []
        r['hosts'] = []
        r['ips'].extend(route['ips'])
        r['domains'].extend(route['domains'])
        r['hosts'].extend(route['hosts'])        
        return r    
     
    @staticmethod
    def render_html_body(html_body):
        # type: (str) -> unicode
        """
        Render html body to plain text plain
        :param html_body: {str} The HTML body of the email
        :return: {unicode} Plain text rendered HTML
        """

        def build_html_rendered():
            """
            Create a HTML2Text object
            :return: {html2text.HTML2Text} The HTMl2Text object
            """
            renderer = HTML2Text()
            renderer.ignore_tables = True
            #renderer.protect_links = True
            renderer.ignore_images = False
            #renderer.ignore_links = False
            renderer.body_width = 5000
            return renderer

        try:
            html_renderer = build_html_rendered()
            return html_renderer.handle(html_body)
        except:
            # HTML2Text is not performing well on non-ASCII str. On failure - try to decode the str to unicode
            # using utf8 encoding. If failed - return a proper message.
            try:
                # HTML2Text object shouldn't be used twice - it can cause problems and errors according to google
                # Therefore rebuild the object
                html_renderer = build_html_rendered()
                return html_renderer.handle(html_body)
            except Exception as e:
                return "Failed rendering HTML. Error: {}".format(e)
        
class ParsedEmail(object):
    def __init__(self, body=None, header=None, attachments=[]):
        self.body = body
        self.header = header
        self.attachments = attachments
        
    def to_json(self):
        return EmailUtils.export_to_json(self.__dict__)
    
class Headers(object):
    def __init__(self, to=None, _from=None, subject=None, cc=[], bcc=[], reply_to = None, return_path = None, date=None, delivered_to=None, header={}, transport=None, sending=[], receiving=[], received=[], parsed_entities={}):
        self.to = to
        self._from = _from
        self.subject = None
        self.cc = cc
        self.bcc = bcc
        self.date = date
        self.delivered_to = delivered_to
        self.header = header
        self.reply_to = reply_to
        self.return_path = return_path
        self.transport = transport
        self.sending = sending
        self.receiving = receiving
        self.received = received
        self.parsed_entities = parsed_entities

        #for (k, v) in kwargs.items():
        #    setattr(self, k, v)
    
    def __iter__(self):
        self.rename_from()
        return self.__dict__
        
            
    def to_json(self):
        return EmailUtils.export_to_json(self.__dict__)

    def rename_from(self, old_attribute_name="_from", new_attribute_name="from"):
        setattr(self, new_attribute_name, getattr(self, old_attribute_name))
        delattr(self, old_attribute_name)

class EmailBody(object):
    def __init__(self, logger=None, email_utils=None):
        self.logger = logger
        self.email_utils = email_utils
        
    
    def body(self, msg, content_type):
        body_json = {
            'content_type': content_type,
            'content': msg if msg is not None else '',
            'hash': hashlib.sha256(str(msg).encode('utf-8')).hexdigest()
        }
        body_json['parsed_entities'] = self.parse_body(msg) if msg is not None else []
        return body_json


            
    def parse_body(self, body):
        '''This will parse a body and observed IOCs '''
        parsed = []
        _parsed = {}
        entity_list = []
        _entities = {}
        for body_slice in self.string_sliding_window_loop(body):
            parsed = self.email_utils.parsed_entities(body_slice)
            for parsed_entity in parsed:
                found = 0
                for _entity in entity_list:
                    if _entity['identifier'] == parsed_entity['identifier'] and _entity['entity_type'] == parsed_entity['entity_type']:
                        found = 1
                        break
                if found == 0:
                    entity_list.append(parsed_entity)
        return entity_list
    

        
     
        
    @staticmethod    
    def string_sliding_window_loop(body: str, slice_step: int = 50000) -> typing.Iterator[str]:
        """Yield a more or less constant slice of a large string.
        If we start directly a *re* findall on 500K+ body we got time and memory issues.
        If more than the configured slice step, lets cheat, we will cut around the thing we search "://, @, ."
        in order to reduce regex complexity.
        Args:
            body: Body to slice into smaller pieces.
            slice_step: Slice this number or characters.
        Returns:
            typing.Iterator[str]: Sliced body string.
        """
        body_length = len(body)
        if body_length <= slice_step:
            yield body

        else:
            ptr_start = 0
            for ptr_end in range(slice_step, body_length, slice_step):
                if ' ' in body[ptr_end - 1:ptr_end]:
                    while not (WINDOW_SLICE_REGEX.match(body[ptr_end - 1:ptr_end]) or ptr_end > body_length):
                        if ptr_end > body_length:
                            ptr_end = body_length
                            break
                        ptr_end += 1
            yield body[ptr_start:ptr_end]
            ptr_start = ptr_end


            

class MSGParser(object):
    def __init__(self, msg_extractor, msg_parser, email_utils=None):
        self.msg_extractor = msg_extractor
        self.msg_parser = msg_parser
        self.email_utils = email_utils


    def parse_headers(self):
        _headers = {}
        transport = []
        transport_stopped = False
        
        headers = Headers()
        
        headers.subject = self.msg_parser['Subject'] if 'Subject' in self.msg_parser else self.msg_extractor.subject # use the value from parser over extractor
        headers.parsed_entities = self.email_utils.parsed_entities(headers.subject)
        headers.to = self.to()
        headers._from = self.from_header()
        
        headers.cc = self.msg_extractor.cc
        headers.bcc = self.msg_extractor.bcc
        headers.date = self.msg_extractor.date
        #headers.reply_to = self.msg_extractor.reply_to
        
        
        for header, value in self.msg_extractor.header._headers[::-1]:
            
            #if self.stop_transport and header.lower() == self.stop_transport.lower():
            #    transport_stopped = True
            if header.lower() == "received" and not transport_stopped:
                
                line = str(value).lower()
                received_line_flat = re.sub(r'(\r|\n|\s|\t)+', ' ', line, flags=re.UNICODE)
                
                parsed_routing = EmailParserRouting.parserouting(received_line_flat)
                headers.received.append(parsed_routing)
                
                from_routing = EmailUtils.parse_routing(parsed_routing.get('from', []))
                sending_route = EmailUtils.routing_entities(from_routing)
                if len(sending_route['ips']) > 0 or len(sending_route['domains']) > 0 or len(sending_route['hosts']) > 0:                    
                    headers.sending.append(sending_route)
                    
                to_routing = EmailUtils.parse_routing(parsed_routing.get('by', []))
                receiving_route = EmailUtils.routing_entities(to_routing)
                if len(receiving_route['ips']) > 0 or len(receiving_route['domains']) > 0 or len(receiving_route['hosts']) > 0:
                    headers.receiving.append(receiving_route)
                    
                
            #if self.is_whitelist:
            #    if header.lower() in self.blacklist:
            #        if header.lower() not in _headers:
            #            _headers[header.lower()] = []
            #            _headers[header.lower()].append(value)
            
            #if header.lower() not in self.blacklist:
            if header.lower() not in _headers:
                _headers[header.lower()] = []
            _headers[header.lower()].append(value)
        headers.header = _headers
        return headers
    
    def from_header(self):
        from_smtp = 'null'
        if 'ReceivedByAddressType' in self.msg_parser:
            if self.msg_parser.get('SenderAddressType') == 'EX':
                from_smtp = 'SenderSmtpAddress'
            else:
                from_smtp = 'SenderEmailAddress'
        if from_smtp in self.msg_parser:
            _from = self.msg_parser.get(from_smtp)
        else:
            _from = self.msg_extractor.sender
            
        display_name, from_email = parseaddr(_from)
        return from_email
        
        
    
    def to(self):
        to_smtp = 'null'
        to = None
        if 'ReceivedByAddressType' in self.msg_parser:
            if self.msg_parser['ReceivedByAddressType'] == 'EX':
                to_smtp = 'ReceivedBySmtpAddress'
            else:
                to_smtp = 'ReceivedByEmailAddress'
        if to_smtp in self.msg_parser:
            to = self.msg_parser.get(to_smtp)
        else:
            to = self.msg_extractor.to
        
        display_name, to_email = parseaddr(to)
        return [to_email]

    def parse(self):
        parsed_msg = {"header": None, "body": [], "attachments": []}
        headers = self.parse_headers()
        headers.rename_from()
        parsed_msg['header'] = headers.__dict__
        email_body = EmailBody(email_utils=self.email_utils)

        parsed_msg['body'].append(email_body.body(self.msg_extractor.body, 'text/plain'))
        if self.msg_extractor.htmlBody:
            try:
                parsed_msg['body'].append(email_body.body(self.msg_extractor.htmlBody.decode(), 'text/html'))
            except:
                parsed_msg['body'].append(email_body.body(self.msg_extractor.htmlBody, 'text/html'))

        attachments = []
        for _attachment in self.msg_extractor.attachments:
            msox_obj = None

            for msox_attachments in self.msg_parser['attachments']:

                if self.msg_parser['attachments'][msox_attachments]['AttachFilename'] == _attachment.shortFilename:
                    msox_obj = self.msg_parser['attachments'][msox_attachments]
            if _attachment.type == "msg":

                parser = MSGParser(_attachment.data, msox_obj, email_utils=self.email_utils)
                parsed_nested_msg = parser.parse()
                parsed_nested_msg['source_file'] = f"{msox_obj['AttachFilename']}.msg"
                if 'attached_emails' in parsed_msg:
                    parsed_msg['attached_emails'].append(parsed_nested_msg)
                else:
                    parsed_msg['attached_emails'] = []
                    parsed_msg['attached_emails'].append(parsed_nested_msg)

            elif 'AttachLongFilename' in msox_obj:
                parsed_msg['attachments'].append(
                    EmailUtils.attachment(filename=msox_obj['AttachLongFilename'], content=_attachment.data))

        return parsed_msg
            
class EMLParser(object):
    def __init__(self, msg, email_utils = None):
        self.msg = msg
        self.email_utils = email_utils
        pass
    
    def parse_headers(self):
        # parse and decode subject
        headers = Headers()
        
        subject = self.msg.get('subject', '')
        headers.subject = EmailUtils.decode_field(subject)
        
        
        headers.parsed_entities = self.email_utils.parsed_entities(headers.subject)
        
        msg_header_field = str(self.msg.get('from', '')).lower()
        if msg_header_field != '':
            m = EMAIL_REGEX.search(msg_header_field)
            if m:
                headers._from = m.group(1)
            else:
                from_ = email.utils.parseaddr(self.msg.get('from', '').lower())
                headers._from = from_[1]
        # parse and decode "to"
        headers.to = self.header_email_list('to')
        # parse and decode "cc"
        headers.cc = self.header_email_list('cc')
        headers.bcc = self.header_email_list('bcc')
        try:
            headers.reply_to = email.utils.parseaddr(self.header_email_list('reply-to')[0])[1]
        except:
            pass
        
        try:
            headers.return_path = email.utils.parseaddr(self.header_email_list('return_path')[0])[1]
        except:
            pass
        # parse and decode delivered-to
        headers.delivered_to = self.header_email_list('delivered-to')

        if 'date' in self.msg:
            try:
                msg_date = self.msg.get('date')
            except TypeError:
                headers.date = dateutil.parser.parse('1970-01-01T00:00:00+0000')
                self.msg.replace_header('date', headers.date)
            else:
                headers.date = EmailUtils.string2date(msg_date)

        else:
            # If date field is absent...
            headers.date = dateutil.parser.parse('1970-01-01T00:00:00+0000')
            
        try:
            for received_line in self.msg.get_all('received', []):
                line = str(received_line).lower()

                received_line_flat = re.sub(r'(\r|\n|\s|\t)+', ' ', line, flags=re.UNICODE)

                parsed_routing = EmailParserRouting.parserouting(received_line_flat)
                headers.received.append(parsed_routing)
                
                from_routing = EmailUtils.parse_routing(parsed_routing.get('from', []))
                sending_route = EmailUtils.routing_entities(from_routing)
                if len(sending_route['ips']) > 0 or len(sending_route['domains']) > 0 or len(sending_route['hosts']) > 0:                    
                    headers.sending.append(sending_route)
                    
                to_routing = EmailUtils.parse_routing(parsed_routing.get('by', []))
                receiving_route = EmailUtils.routing_entities(to_routing)
                if len(receiving_route['ips']) > 0 or len(receiving_route['domains']) > 0 or len(receiving_route['hosts']) > 0:
                    headers.receiving.append(receiving_route)
                
        except TypeError:  # Ready to parse email without received headers.
            print('Exception occurred while parsing received lines.')
        
        # Get the all the remaining header values.
        header = {}
        for k in set(self.msg.keys()):
          
            k = k.lower()  # Lot of lower, pre-compute...
            decoded_values = []
            try:
                for value in self.msg.get_all(k, []):
                    if value:
                        decoded_values.append(value)
            except (IndexError, AttributeError, TypeError):
                # We have hit a field value parsing error.
                # Try to work around this by using a relaxed policy, if possible.
                # Parsing might not give meaningful results in this case!
                print('ERROR: Field value parsing error, trying to work around this!')
                if self.msg.policy == email.policy.compat32:  # type: ignore
                    new_policy = None
                else:
                    new_policy = msg.policy  # type: ignore

                self.msg.policy = email.policy.compat32  # type: ignore
                
                for value in self.msg.get_all(header, []):
                    if value != '':
                        decoded_values.append(value)

                if new_policy is not None:
                    self.msg.policy = new_policy
                    
            if decoded_values:
                if k in header:
                    header[k] += decoded_values
                else:
                    header[k] = decoded_values
                    
        headers.header = header
        return headers
        
    def parse_body(self):
        raw_bodies = self.get_raw_body_text(self.msg)
        email_body = EmailBody(email_utils=self.email_utils)
        body = []
        
        # the body is multi part if more than 1.
        if len(raw_bodies) == 1:
            multipart = False
        else:
            multipart = True
            
        found_txt = 0
        html_body = ''
        for raw_body in raw_bodies:
            
            _content_type, body_value, body_multhead = raw_body
            content_type = self.get_content_type(body_multhead, multipart)
            if content_type == 'text/plain':
                found_txt = 1
            if content_type == 'text/html':
                html_body = body_value
                
                
            body.append(email_body.body(body_value, content_type))
        if found_txt == 0:
            rendered_body = EmailUtils.render_html_body(html_body)
            body.append(email_body.body(rendered_body, 'text/plain'))
            
        return body
        
    def parse(self):
        attachments = self.traverse_multipart(self.msg, counter=0)
        headers = self.parse_headers()
        body = self.parse_body()
        headers.rename_from()
        return {"header": headers.__dict__, "body": body, "attachments": attachments }
        
    
    def traverse_multipart(self, msg, counter):
        """Recursively traverses all e-mail message multi-part elements and returns in a parsed form as a dict.

        Args:
            msg (email.message.Message): An e-mail message object.
            counter (int, optional): A counter which is used for generating attachments
                file-names in case there are none found in the header. Default = 0.

        Returns:
            dict: Returns a dict with all original multi-part headers as well as generated hash check-sums,
                date size, file extension, real mime-type.
        """
        attachments = []

        if msg.is_multipart():
            if 'content-type' in msg and msg.get_content_type() == 'message/rfc822':
                attachments.append(self.prepare_attachment(msg, counter))

            else:
                for part in msg.iter_attachments():
                    attachments.extend(self.traverse_multipart(part, counter))
        else:
            parsed_attachment = self.prepare_attachment(msg, counter)
            if parsed_attachment:
                return [self.prepare_attachment(msg, counter)]
            return []

        return attachments
    
    
    def prepare_attachment(self, msg, counter):
        """Extract meta-information from a multipart-part.

        Args:
            msg (email.message.Message): An e-mail message object.
            counter (int, optional): A counter which is used for generating attachments
                file-names in case there are none found in the header. Default = 0.

        Returns:
            dict: Returns a dict with original multi-part headers as well as generated hash check-sums,
                date size, file extension, real mime-type.
        """
        attachment = {}
        
        # In case we hit bug 27257, try to downgrade the used policy
        try:
            
            lower_keys = [k.lower() for k in msg.keys()]
            
        except AttributeError:
            former_policy: email.policy.Policy = msg.policy  # type: ignore
            msg.policy = email.policy.compat32  # type: ignore
            lower_keys = [k.lower() for k in msg.keys()]
            msg.policy = former_policy  # type: ignore

        if ('content-disposition' in lower_keys and msg.get_content_disposition() != 'inline') \
            or msg.get_content_maintype() != 'text':
            # if it's an attachment-type, pull out the filename
            # and calculate the size in bytes
            #charset = msg.get_content_charset()
            filename = msg.get_filename('')
            if msg.get_content_type() == 'message/rfc822':
                payload = msg.get_payload()
                if len(payload) > 1:
                    self.logger.info(
                        'More than one payload for "message/rfc822" part detected. This is not supported, please report!')

                try:
                    data = payload[0].as_bytes()
                except UnicodeEncodeError:
                    data = payload[0].as_bytes(policy=email.policy.compat32)

                file_size = len(data)
            else:
                data2 = msg.get_payload(decode=False)
                data = msg.get_payload(decode=True)
                file_size = len(data)
            
            
            if filename == '':
                filename = 'part-{0:03d}'.format(counter)
            else:
                filename = EmailUtils.decode_field(filename)

            file_id = str(uuid.uuid1())
            attachment['filename'] = filename
            attachment['size'] = file_size
        
            # os.path always returns the extension as second element
            # in case there is no extension it returns an empty string
            extension = os.path.splitext(filename)[1].lower()
            if extension:
                # strip leading dot
                attachment['extension'] = extension[1:]

            attachment['hash'] = EmailUtils.get_file_hash(data)
            if len(data) != 0:
                
                mime_type, mime_type_short = EmailUtils.get_mime_type(data)

                if not (mime_type is None or mime_type_short is None):
                    attachment['mime_type'] = mime_type
                    attachment['mime_type_short'] = mime_type_short
                else:
                    if magic is not None:
                        print('Error determining attachment mime-type - "{}"'.format(file_id))
                    
                try:
                    oid = OleId.OleID(data=data)
                    indicators = oid.check()
                    attachment['ole_data'] = []
                    for i in indicators:
                        ole_indicator = {}
                        ole_indicator['id'] = i.id
                        ole_indicator['value'] = i.value
                        ole_indicator['name'] = i.name
                        ole_indicator['description'] = i.description
                        ole_indicator['risk'] = i.risk
                        ole_indicator['hide_if_false'] = i.hide_if_false
                        attachment['ole_data'].append(ole_indicator)    
                    
                except Exception as e:
                    print(f" failed in ole data: {e}")
                    pass
            else:
                print("No data in attachment")

            
            attachment['raw'] = (base64.b64encode(data)).decode('utf-8')

            ch: typing.Dict[str, typing.List[str]] = {}
            for k, v in msg.items():
                k = k.lower()
                v = str(v)

                if k in ch:
                    ch[k].append(v)
                else:
                    ch[k] = [v]

            attachment['content_header'] = ch
            counter += 1
            return attachment

 
    
      
        
            
    @staticmethod
    def get_content_type(headers, multipart=False):
        ch = {}
        content_type = ""
        for k, v in headers:
            # make sure we are working with strings only
            v = str(v)
            k = k.lower()  # Lot of lowers, pre-compute :) .
            if multipart:
                if k in ch:
                    ch[k].append(v)
                else:
                    ch[k] = [v]
            else:  # if not multipart, store only content-xx related header with part
                if k.startswith('content'):  # otherwise, we got all header headers
                    if k in ch:
                        ch[k].append(v)
                    else:
                        ch[k] = [v]
        val = ch.get('content-type')
        if val:
            header_val = val[-1]
            content_type = header_val.split(';', 1)[0].strip()
        return content_type
        
    def get_raw_body_text(self, msg):
        #TODO: This might cause some dupe bodys due to the multiparty .html stuff.
        """This method recursively retrieves all e-mail body parts and returns them as a list.

        Args:
            msg (email.message.Message): The actual e-mail message or sub-message.

        Returns:
            list: Returns a list of sets which are in the form of "set(encoding, raw_body_string, message field headers)"
        """
        raw_body= []
        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_type() != 'message/rfc822':
                    raw_body.extend(self.get_raw_body_text(part))
        else:
            # Treat text document attachments as belonging to the body of the mail.
            # Attachments with a file-extension of .htm/.html are implicitly treated
            # as text as well in order not to escape later checks (e.g. URL scan).

            try:
                filename = msg.get_filename('').lower()
            except (binascii.Error, AssertionError):
                print(
                    'Exception occurred while trying to parse the content-disposition header. Collected data will not be complete.')
                filename = ''

            
            if ('content-disposition' not in msg and msg.get_content_maintype() == 'text') \
                or (filename.endswith('.html') or filename.endswith('.htm')) \
                or ('content-disposition' in msg and msg.get_content_disposition() == 'inline'
                    and msg.get_content_maintype() == 'text'):
                encoding = msg.get('content-transfer-encoding', '').lower()

                charset = msg.get_content_charset()
                if charset is None:
                    raw_body_str = msg.get_payload(decode=True)
                    raw_body_str = EmailUtils.decode_string(raw_body_str, None)
                else:
                    try:
                        raw_body_str = msg.get_payload(decode=True).decode(charset, 'ignore')
                    except (LookupError, ValueError):
                        print(f"lookup error: {LookupError}, value error: {ValueError}.")
                        
                        raw_body_str = msg.get_payload(decode=True).decode('ascii', 'ignore')

                # In case we hit bug 27257 or any other parsing error, try to downgrade the used policy
                try:
                    raw_body.append((encoding, raw_body_str, msg.items()))
                except (AttributeError, TypeError):
                    former_policy: email.policy.Policy = msg.policy  # type: ignore
                    msg.policy = email.policy.compat32  # type: ignore
                    raw_body.append((encoding, raw_body_str, msg.items()))
                    msg.policy = former_policy  # type: ignore

        return raw_body
        

        


    def header_email_list(self, header):
        """Parses a given header field like to, from, cc with e-mail addresses to a list of e-mail addresses."""

        if self.msg is None:
            raise ValueError('msg is not set.')

        field = email.utils.getaddresses(self.msg.get_all(header, []))
        
        return_field = []

        for m in field:
            if not m[1] == '':
                if EMAIL_TLD_REGEX.match(m[1]):
                    return_field.append(m[1].lower())
                    
        return return_field    
        
class EmailManager(object):
    
    
    def __init__(self, siemplify=None, logger=None, custom_regex=None):
        self.logger = logger
        self.siemplify = siemplify
        self.attachments = []
        self.attached_emails = []
        self.custom_regex = custom_regex

    def traverse_attachments(self, attachment_name, content_bytes, nested_level):
        if EmailUtils.is_ole_file(content_bytes):
            try:
                self.logger.info('trying parse msg')
                parsed = self.parse_msg(content_bytes)
                self.logger.info('parsed MSG')
                self.logger.info(parsed)

            except Exception as e:
                self.logger.info(e)
                return
        else:
            parsed = self.parse_eml(content_bytes)

        if not parsed:
            return
        parsed['source_file'] = attachment_name
        parsed['level'] = nested_level

        if 'attached_emails' in parsed:
            nl = nested_level
            for attached_eml in parsed['attached_emails']:
                nl = nl + 1
                attached_eml['level'] = nl
                self.attached_emails.append(attached_eml)
            del parsed['attached_emails']
        for attachment in parsed['attachments']:
            attachment['level'] = nested_level

            self.attachments.append(attachment.copy())
            # if attachment['mime_type_short'] == 'message/rfc822' or attachment['mime_type_short'] == 'Composite Document File V2 Document, No summary info':
            decoded_data = base64.b64decode(attachment['raw'])
            p_email = self.traverse_attachments(attachment['filename'], decoded_data, nested_level + 1)
            if p_email:
                attachment['parsed_email'] = p_email
                attached_email = attachment["parsed_email"].copy()
                attached_email['source_file'] = attachment['filename']
                extension = os.path.splitext(attachment['filename'])[1].lower()
                if extension:
                # strip leading dot
                    attached_email['extension'] = extension[1:]
                else:
                    attached_email['extension'] = ''

                for nested_attach in attached_email['attachments']:
                    if 'parsed_email' in nested_attach:
                        del nested_attach['parsed_email']
                if  attached_email['extension'] != "ics":
                    self.attached_emails.append(attached_email)

            del attachment['raw']

        return parsed
    
    def parse_email(self, attachment_name, content_bytes, nested_level=0):
        parsed = self.traverse_attachments(attachment_name, content_bytes, nested_level)
        if not parsed:
            return
        _email = {}
        _email['result'] = parsed
        _email['attachments'] = self.attachments
        _parsed = parsed.copy()
        for nested_attach in _parsed['attachments']:
            if 'parsed_email' in nested_attach:
                del nested_attach['parsed_email']
        self.attached_emails.append(_parsed)
        _email['attached_emails'] = self.attached_emails
        return _email
                
    def parse_msg(self, message):
        #
        msg_extractor = extract_msg.openMsg(message)
        
        # MsOxMessage handles the filenames better.
        msox = MsOxMessage(message)
        msg_parser = msox._message.as_dict()
        email_utils = EmailUtils(custom_regex=self.custom_regex)
        parser = MSGParser(msg_extractor, msg_parser, email_utils=email_utils)
        return parser.parse()
        
    def parse_eml(self, eml_file):
        msg = email.message_from_bytes(eml_file, policy=email.policy.default)
        email_utils = EmailUtils(custom_regex=self.custom_regex)
        if not msg: 
            return
        parser = EMLParser(msg=msg, email_utils=email_utils)
        return parser.parse()
        
    def get_alert_entity_identifiers(self):
        self.siemplify.load_case_data()
        return [entity.identifier for alert in self.siemplify.case.alerts for entity in alert.entities]

    def get_alert_entities(self):
        self.siemplify.load_case_data()
        return [entity for alert in self.siemplify.case.alerts for entity in alert.entities]        

    def create_entity_with_relation(self,  new_entity, linked_entity, entity_type, linked_entity_type=None, is_primary=False, is_directional=False):
        new_entity = new_entity.upper().strip()
        linked_entity = linked_entity.upper().strip()
        self.siemplify.LOGGER.info(f"New entity: {new_entity}, linked_entity: {linked_entity}.")
        current_entities = self.get_alert_entity_identifiers()
        self.siemplify.LOGGER.info(f"current entities: {current_entities}.")
        if linked_entity not in current_entities:
            self.siemplify.LOGGER.info(f"linked_entity {linked_entity} is not in case, adding it.")
            self.siemplify.add_entity_to_case(linked_entity, linked_entity_type, False, False,
                                                 False, False, {})
            #self.siemplify.load_case_data()
            
        json_payload = {
            "caseId": self.siemplify.case_id,
            "alertIdentifier": self.siemplify.alert_id,
            "entityType": entity_type,
            "isPrimaryLink": is_primary,
            "isDirectional": is_directional,
            "typesToConnect": [],
            "entityToConnectRegEx": "{}$".format(re.escape(linked_entity)),
            "entityIdentifier": new_entity
        }
        payload = json_payload.copy()
        self.siemplify.LOGGER.info(f"Creating {new_entity}:{entity_type} and linking it to {linked_entity}.")
        created_entity = self.siemplify.session.post(EXTEND_GRAPH_URL.format(self.siemplify.API_ROOT), json=json_payload)
        created_entity.raise_for_status()
        
    
    def build_entity_list(self, email, entity_type, exclude_regex=None):
        
        entities = []
        entities_list = []
        _found_entities = {}
        current_entities = self.get_alert_entity_identifiers()
        for body in email['body']:
            for _entity in body['parsed_entities']:

                if _entity['entity_type'] == entity_type and _entity['identifier'] not in _found_entities:
                    if exclude_regex:
                        if not re.search(exclude_regex, _entity['identifier']):
                            entities_list.append(_entity['identifier'])
                    else:
                        entities_list.append(_entity['identifier'])
                    _found_entities[_entity['identifier']] = 1
        
        
        if 'parsed_entities' in email['header']:
            for _entity in email['header']['parsed_entities']:
                if _entity['entity_type'] == entity_type and _entity['identifier'] not in _found_entities:
                    if exclude_regex:
                        if not re.search(exclude_regex, _entity['identifier']):
                            entities_list.append(_entity['identifier'])
                    else:
                        entities_list.append(_entity['identifier'])
                    _found_entities[_entity['identifier']] = 1
        
        # remove any urls that match a url with http(s)://
        if entity_type == "DestinationURL":
            #_entities_list = entities_list.copy()
            _entities_list = {x:x for x in entities_list}
            for entity in entities_list:
                if entity:
                    if not re.search("^https?", entity):
                        if f"https://{entity}" in _entities_list or f"http://{entity}" in _entities_list:
                            del _entities_list[entity]
                else:
                    del _entities_list[entity]
                    
            entities_list = [key for key in _entities_list.keys()]

            
        # Remove any URLs that end in / and already exist in the case without the slash.
        for new_entity in entities_list:
            if new_entity.rstrip("/").upper() in current_entities:
                entities_list.remove(new_entity)
            elif f"{new_entity}/".upper() in current_entities:
                entities_list.remove(new_entity)
        return entities_list
    
    def create_entities(self, create_base_entities, create_observed_entity_types, exclude_regex, email, fang_entities):
        #create users out of to and from
        #create email subject out of subject
        #create file out of attachment
        #hash from file
        #Create entitys of FROM and TO
        if not email['header']['subject']:
            if 'message_id' in email['header']['header']:
                email['header']['subject'] = email['header']['header']['message-id']
            else:
                email['header']['subject'] = 'MISSING SUBJECT'
        if create_base_entities:
            
            for _to in email['header']['to']:
                if _to != '':
                    
                    self.create_entity_with_relation(email['header']['from'], _to, "USERUNIQNAME", "USERUNIQNAME", True, True)
                    if email['header']['subject']:
                        self.create_entity_with_relation(email['header']['subject'], _to, "EMAILSUBJECT", "USERUNIQNAME", False, False)
                else:
                    self.siemplify.add_entity_to_case(email['header']['subject'].upper().strip(), "EMAILSUBJECT", False, False,
                                                 False, False, {})
            if isinstance(email['header']['cc'], list):
                for _to in email['header']['cc']:
                    if _to != '':
                    
                        self.create_entity_with_relation(email['header']['from'], _to, "USERUNIQNAME", "USERUNIQNAME", True, True)
                        if email['header']['subject']:
                            self.create_entity_with_relation(email['header']['subject'], _to, "EMAILSUBJECT", "USERUNIQNAME", False, False)
                    else:
                        self.siemplify.add_entity_to_case(email['header']['subject'].upper().strip(), "EMAILSUBJECT", False, False,
                                                 False, False, {})
            else:
                if email['header']['cc'] != '' and  email['header']['cc'] != None:
                    self.create_entity_with_relation(email['header']['from'], email['header']['cc'], "USERUNIQNAME", "USERUNIQNAME", True, True)
                    if email['header']['subject']:
                        self.create_entity_with_relation(email['header']['subject'], email['header']['cc'], "EMAILSUBJECT", "USERUNIQNAME", False, False)
                
            if isinstance(email['header']['bcc'], list):
                for _to in email['header']['bcc']:
                    if _to != '':
                        self.create_entity_with_relation(email['header']['from'], _to, "USERUNIQNAME", "USERUNIQNAME", True, True)
                        if email['header']['subject']:
                            self.create_entity_with_relation(email['header']['subject'], _to, "EMAILSUBJECT", "USERUNIQNAME", False, False)
                    else:
                        self.siemplify.add_entity_to_case(email['header']['subject'].upper().strip(), "EMAILSUBJECT", False, False,
                                                     False, False, {})
            else:
                if email['header']['bcc'] != '' and  email['header']['bcc'] != None:
                    self.create_entity_with_relation(email['header']['from'], email['header']['bcc'], "USERUNIQNAME", "USERUNIQNAME", True, True)
                    if email['header']['subject']:
                        self.create_entity_with_relation(email['header']['subject'], email['header']['bcc'], "EMAILSUBJECT", "USERUNIQNAME", False, False)
        
        entity_types = [getattr(EntityTypes, a) for a in dir(EntityTypes) if not a.startswith('__')]

        
        for entity_type in entity_types:
            
            #self.siemplify.LOGGER.info(f"Checking if {ioc_type} is enabled.")    
            
            if entity_type in create_observed_entity_types.lower() or 'all' in create_observed_entity_types.lower():
                
                #self.siemplify.LOGGER.info(f"Creating any {ioc_type} IOCs from {email['header']['subject']}")
                entities = self.build_entity_list(email, entity_type, exclude_regex)
                self.siemplify.LOGGER.info(f"Got these {entity_type} entities to create: {entities}.")
                for entity in entities:
                    # If the fang_entities option is set,  attempt to fang, decode url defence, and decode safelinks
                    if fang_entities:
                        
                        entity = ioc_fanger.fang(entity)
                        if (("urldefense" in entity.lower()) or ("proofpoint" in entity.lower())) and entity_type == "DestinationURL":
                            # decode any URLDefense URLs
                            urldefense_decoder = URLDefenseDecoder()
                            try:
                                entity = urldefense_decoder.decode(entity)
                            except:
                                pass
                        if "safelinks.protection.outlook.com" in entity.lower() and entity_type == "DestinationURL":
                            # if the URL contains safelinks, use urlparse and parse_qs to extract to the correct URL
                            try:
                                entity = parse_qs(urlparse(entity.lower()).query)['url'][0]
                            except:
                                pass
                            
                        
                    self.create_entity_with_relation( entity, email['header']['subject'], entity_type, "EMAILSUBJECT", False, False)
               
        self.create_file_entities(email['attachments'], email['header']['subject'])
        pass
        
        
    def create_file_entities(self,  attachments, subject_entity):
        new_entities_w_rel = {}
        updated_entities = []
        alert_entities = self.get_alert_entities()
        #print(f"The following entities are already in the case: {alert_entities}.")
        for file_entity in attachments:
            entity_identifier = str(file_entity['filename'].strip()).upper()
            try:
                properties = {}
                properties = dict_to_flat(file_entity)
                
                del properties['filename']
                if 'attached_email' in properties:
                    del properties['attached_email']
                if 'raw' in properties:
                    del properties['raw']
                    
                # This is because the ETL layer removes the extension from the filename when its attached.  DUMB
                name, attachment_type = os.path.splitext(entity_identifier)
                for a in alert_entities:
                    if a.identifier == name and a.entity_type == "FILENAME":
                        entity_identifier = name
                        break
                    
                
                if subject_entity:
                    self.logger.info(f"creating with relation: {entity_identifier} to {subject_entity}")
                   #self.logger.info(f"No subject entity. Linking {entity_identifier} to {subject_entity}  ")
                    self.create_entity_with_relation( entity_identifier, subject_entity, "FILENAME", "EMAILSUBJECT", False, False)
                self.create_entity_with_relation( file_entity['hash']['md5'], entity_identifier, "FILEHASH", "FILENAME", False, False)
                new_entities_w_rel[entity_identifier] = properties
                source_props = {}
                source_props['source_file'] = entity_identifier
                new_entities_w_rel[file_entity['hash']['md5']] = source_props
                
                
            except Exception as e:
                self.logger.error(e)
                raise
        if new_entities_w_rel:
            self.siemplify.load_case_data()
            for new_entity in new_entities_w_rel:
                for entity in self.get_alert_entities():
                    if new_entity.strip() == entity.identifier.strip():
                        entity.additional_properties.update(new_entities_w_rel[new_entity])
                        updated_entities.append(entity)
                        break
            self.logger.info(f"updating file entity properties: {updated_entities}")
            self.siemplify.update_entities(updated_entities)     
        
        
    def add_attachment(self, filename,  base64_blob, case_id, alert_identifier, description=None, is_favorite=False):
        """
        add attachment
        :param file_path: {string} file path
        :param case_id: {string} case identifier
        :param alert_identifier: {string} alert identifier
        :param description: {string} attachment description
        :param is_favorite: {boolean} is attachment favorite
        :return: {dict} attachment_id
        """
        name, attachment_type = os.path.splitext(os.path.split(filename)[1])
        if not attachment_type:
            attachment_type = ".noext"
        attachment = Attachment(case_id, alert_identifier, base64_blob, attachment_type, name, description, is_favorite, len(base64.b64decode(base64_blob)), len(base64_blob))
        attachment.case_identifier = case_id
        attachment.alert_identifier = alert_identifier
        address = "{0}/{1}".format(self.siemplify.API_ROOT, "external/v1/sdk/AddAttachment?format=snake")
        response = self.siemplify.session.post(address, json=attachment.__dict__)
        try:
            self.siemplify.validate_siemplify_error(response)
        except Exception as e:
            if "Attachment size" in e.message:
                raise Exception("Attachment size should be < 5MB. Original file size: {0}. Size after encoding: {1}.".
                                format(attachment.orig_size, attachment.size))
