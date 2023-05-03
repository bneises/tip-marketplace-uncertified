from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler, convert_dict_to_json_result_dict
from SiemplifyDataModel import EntityTypes
import dns.resolver, dns.reversename
from dns.resolver import Resolver


SCRIPT_NAME = "QueryDNS"

@output_handler

def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
#    record_type = siemplify.parameters.get("Record Type")
    dns_servers = siemplify.parameters.get("DNS Servers")
#    dns_servers = '10.10.10.90', '1.1.1.1'
#    domain_suffix = siemplify.parameters.get("FQDN suffix")
    
    output_message = "No address or hostname found"
    server_list = dns_servers.split(',')
    
    
    json_results = {}
    res = dns.resolver.Resolver(configure=False)
#    res.timeout = 20.0
#    res.nameservers = [dns_servers]
#    res.nameservers = ['10.10.10.90']
    for entity in siemplify.target_entities:
        if entity.entity_type == EntityTypes.ADDRESS:
#            addr = dns.reversename.from_address(entity.identifier)
#            siemplify.LOGGER.info("Reverse name is: " + str(addr))
            for server in server_list:
                server = server.strip()
                res.nameservers = [server]
                try:
                    siemplify.LOGGER.info("--- Checking {} for a reverse DNS entry for IP {} ---".format(server, entity.identifier))
                    answer = res.resolve_address(entity.identifier)
                    
                    entityidentifier = entity.identifier
#                answer = res.query(addr, record_type)
#                siemplify.LOGGER.info("A reverse name PTR record for " + entity.identifier + " was found on server " + server +)

                    if answer:
                        siemplify.LOGGER.info("A reverse name PTR record for {} was found on DNS server {}".format(entity.identifier, server))
                        ptr_record = "PTR"
                        #json_results[entity.identifier] = {ptr_record: {server: str([x for x in answer])}}
                        #json_results[entity.identifier] = {server: {'Type': ptr_record, 'Response': answer.rrset[0], 'DNS Server': server}}
                        if entityidentifier not in json_results:
                            json_results[entityidentifier] = []
                        json_results[entityidentifier].append(
                            {'Type': ptr_record, 'Response': answer.rrset[0], 'DNS Server': server})
                            
                        output_message = "Results Found"
#            except dns.resolver.NoAnswer as err:
#                siemplify.LOGGER.error(err)
#                siemplify.LOGGER.error("########")
#                output_message = "No answer section"
#            except dns.exception.Timeout as err:
#                siemplify.LOGGER.error(err)
#                siemplify.LOGGER.error("--------")
#                output_message = "Query timed out"
                except Exception as err:
                    siemplify.LOGGER.exception(err)
#                siemplify.LOGGER.error("********")
                
                
                
        elif entity.entity_type == EntityTypes.HOSTNAME:
            try:
#                answer = res.resolve(entity.identifier)
                entityidentifier = entity.identifier
                outbound_query = dns.message.make_query(entity.identifier,dns.rdatatype.ANY)
                
                
                for server in server_list:
                    try: 
                        server = server.strip()
                        siemplify.LOGGER.info("--- Checking {} for entity {} ---".format(server, entity.identifier))

#                        print("--- Checking with server " + server + " ---")
                
                        answer = dns.query.udp(outbound_query, server)
                    
                        if answer.answer:
                            
                            for i in range(len(answer.answer)):
                                print(
                                    "A record of type {} was found on DNS server {} with a response of {} for entity {}".format(
                                        dns.rdatatype.to_text(answer.answer[i].rdtype), server, answer.answer[i][0],
                                        entity.identifier))

#                            for a in answer.answer:
#                                print(a)
#                print(answer.answer)
                            
#                print(answer.answer[0].rdtype)
#                print(dns.rdataclass.to_text(answer.answer[0].rdtype))
#                            i=0
#                            while(i<len(answer.answer)):
#                                siemplify.LOGGER.info("A record of type {} was found on DNS server {} with a response of {} for entity {}".format(dns.rdatatype.to_text(answer.answer[i].rdtype), server, answer.answer[i][0], entity.identifier))
#                                print(dns.rdatatype.to_text(answer.answer[i].rdtype))
#                                print(answer.answer[i][0])
#                                i += 1
#                print(dns.rdataset.Rdataset.to_text(answer.answer[0]))
#                print(dns.rrset.RRset.to_text(answer.answer[0]))
#                print(answer.answer[0].response)
                
#                        i=0
#                        while(i<len(answer.answer)):
#                            print(answer.answer[i])
#                            i+=1

                                hn_record = dns.rdatatype.to_text(answer.answer[i].rdtype)
                                record_response = str(answer.answer[i][0]).strip('"')
                                #print(record_response)
                        #hn_record = '1'
#                siemplify.LOGGER.info("Found a record of type '" + hn_record + "' for " + entity.identifier)
#                            json_results[entity.identifier] = {hn_record:[x for x in answer.answer]}
                                #json_results[entity.identifier] = {server: {hn_record: {'Type': hn_record, 'Response': record_response, 'DNS Server': server }}}
                                if entityidentifier not in json_results:
                                    json_results[entityidentifier] = []
                                                                    
                                
                                json_results[entityidentifier].append({'Type': hn_record, 'Response': record_response, 'DNS Server': server })
                                
                            output_message = "Results Found"
                        else:
                            siemplify.LOGGER.info("No record found")
                            
                    except Exception as err:
                        siemplify.LOGGER.error(err)
            except Exception as err:
                siemplify.LOGGER.error(err)
#                siemplify.LOGGER.error("@@@@@@@@@")

    if json_results:
        siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_results))
        siemplify.end(output_message, 'true')
    else:
        siemplify.end(output_message, 'false')

if __name__ == "__main__":
    main()