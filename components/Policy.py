import re

class Policy(object):

    def __init__(self,data):
        self.from_node_name = data[0]
        self.from_ipv4 = data[1]
        self.from_ipv6 = data[2]
        self.to_node_name = data[3]
        self.to_ipv4 = data[4]
        self.to_ipv6 = data[5]
        self.servicename = data[6]
        self.src_terminator = data[7]
        self.dst_terminator = data[8]
        self.src_network_id = data[9]
        self.dst_network_id = data[10]
        self.service_dst_ports = data[11]
        self.service_src_ports = data[12]
        self.is_ipv4 = data[13]
        self.is_ipv6 = data[14]
        self.flow_name = data[15]
        self.interface_name = data[16]
        self.fw_rule_id = data[17]
        self.unrelatedtraffic1 = self.src_network_id == self.dst_network_id
        self.unrelatedtraffic2 = self.src_terminator not in ('D-ASR-V',  'D-FW-V') and self.dst_terminator not in ('D-ASR-V', 'D-FW-V') and self.from_node_name != 'ANY'
    
    def current_firewall_rule(self):
    	return self.fw_rule_id


    def unknown_terminator_value(self):
        ret = False
        ret = self.src_terminator == 'N/A' and self.from_node_name.startswith('d-asr-v')
        return ret

    def edit_interface(self):
        ret = '\nedit ' + self.fw_ruleid + 1000
        return ret
        
    def set_srcaddr(self, NID_VDOM, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src):
        any_host = False
        cont = '0'
        ret = ''
        try:
            if self.from_node_name == 'ANY':
                any_host = True
            elif current_vdom == 'dreamhack' and self.src_terminator == 'N/A' and self.from_node_name.startswith('d-asr-v'):
                ret = ('set srcaddr ' + self.from_node_name.upper() + '_' + self.from_ipv4)
                cont = 'src'
                if src == 'host':
                    ret = ('set srcaddr ' + self.from_node_name.upper() + '_' + self.from_ipv4)
                    cont = 'src'
                elif src =='net':
                    ret = ('set srcaddr ' + self.from_node_name.upper() + '_IPV4_NET')
                    cont = 'src'
            elif current_vdom == NID_VDOM[self.src_network_id]:
                if src == 'host':
                    ret = ('set srcaddr ' + self.from_node_name.upper() + '_' + self.from_ipv4)
                    cont = 'src'
                elif src =='net':
                    ret = ('set srcaddr ' + self.from_node_name.upper() + '_IPV4_NET')
                    cont = 'src'
            else:
                if current_vdom == NID_VDOM[self.dst_network_id]:
                    if src == 'host':
                        ret = ('set srcaddr ' + self.from_node_name.upper() + '_' + self.from_ipv4)
                        cont = 'dst'
                    elif src =='net':
                        ret = ('set srcaddr ' + self.from_node_name.upper() + '_IPV4_NET')
                        cont = 'dst'
                else:
                    pass
        except KeyError:
            pass
        return(cont, ret, any_host)

    def set_srcintf(self, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src_or_dest):
        if src_or_dest == 'src':
            ret = '\nset srcintf ' + NIDtoINTERFACE[self.src_network_id][0]
        elif src_or_dest == 'dst':
            if src_network_id in NIDtoINTERFACE:
                ret = '\nset srcintf ' + NIDtoINTERFACE[self.src_network_id][0]
            else:
                ret = '\nset srcintf ' + 'FW-OUT-' + current_vdom.upper()
        else:
            print('Something went terribly wrong')
            ret = ''
        return ret
 
    def set_dstaddr(self, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src_or_dest, dst):	
        if dst == 'host':
            ret = ('\nset srcaddr ' + self.to_node_name.upper() + '_' + self.to_ipv4)
        elif dst =='net':
            ret = ('\nset dstaddr ' + self.to_node_name.upper() + '_IPV4_NET')
        return ret	

    def set_dstintf(self, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src_or_dest):
        if self.dst_network_id in NIDtoINTERFACE:
            ret = '\nset dstintf ' + NIDtoINTERFACE[self.dst_network_id][0]
        else:
            ret = '\nset dstintf ' + 'FW-OUT-' + current_vdom.upper()
        return ret

    def set_service(self):
        ret = ('\nset service ' + self.servicename.upper())
        return ret

    def set_schedule(self):
        ret = '\nset schedule always' 
        ret += '\nnext'
        return ret
    
    def create_any_rule(self, IFACEtoVDOM, current_vdom, NIDtoINTERFACE, dst):
        count = 1
        ret = ''
        for entry in IFACEtoVDOM:
            if dst == 'host':
                end = '_' + self.to_ipv4
            elif dst == 'net':
                end = '_IPV4_NET'
            if current_vdom.upper() == IFACEtoVDOM[count][0]:
                ret += ('\nset srcaddr ANY')
                ret += ('\nset srcintf ') + IFACEtoVDOM[count][1]
                ret += ('\nset dstaddr ') + self.to_node_name.upper() + end
                if self.dst_network_id in NIDtoINTERFACE:
                    ret += ('\nset dstintf ') + str(NIDtoINTERFACE[self.dst_network_id][0])
                    ret += ('\nset service ' + self.servicename.upper())
                    ret += ('\nset schedule always')
                    ret += ('\nnext')
                    count = count + 1
                else:
                    ret += ('\nset dstintf ') + 'FW-OUT-' + current_vdom.upper()
                    ret += ('\nset service ' + self.servicename.upper())
                    ret += ('\nset schedule always')
                    ret += ('\nnext')
                    count = count + 1
            else:
                count = count + 1
                pass
        return ret


    def set_ipv6_srcaddr(self, NID_VDOM, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src):
        any_host = False
        cont = '0'
        ret = ''
        try:
            if self.from_node_name == 'ANY':
                any_host = True
            elif current_vdom == NID_VDOM[self.src_network_id]:
                if src == 'host':
                    ret = ('set srcaddr ' + self.from_node_name.upper() + '_' + self.from_ipv6)
                    cont = 'src'
                elif src =='net':
                    ret = ('set srcaddr ' + self.from_node_name.upper() + '_IPV6_NET')
                    cont = 'src'
            else:
                if current_vdom == NID_VDOM[self.dst_network_id]:
                    if src == 'host':
                        ret = ('set srcaddr ' + self.from_node_name.upper() + '_' + self.from_ipv6)
                        cont = 'dst'
                    elif src =='net':
                        ret = ('set srcaddr ' + self.from_node_name.upper() + '_IPV6_NET')
                        cont = 'dst'
                else:
                    pass
        except KeyError:
            pass
        return(cont, ret, any_host)

    def set_ipv6_dstaddr(self, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src_or_dest, dst):
        if dst == 'host':
            ret = ('\nset srcaddr ' + self.to_node_name.upper() + '_' + self.to_ipv6)
        elif dst =='net':
            ret = ('\nset dstaddr ' + self.to_node_name.upper() + '_IPV6_NET')
        return ret


    def create_any_ipv6_rule(self, IFACEtoVDOM, current_vdom, NIDtoINTERFACE, dst):
        count = 1
        ret = ''
        for entry in IFACEtoVDOM:
            if dst == 'host':
                end = '_' + self.to_ipv6
            elif dst == 'net':
                end = '_IPV6_NET'
            if current_vdom.upper() == IFACEtoVDOM[count][0]:
                ret += ('\nset srcaddr ANY')
                ret += ('\nset srcintf ') + IFACEtoVDOM[count][1]
                ret += ('\nset dstaddr ') + self.to_node_name.upper() + end
                if self.dst_network_id in NIDtoINTERFACE:
                    ret += ('\nset dstintf ') + str(NIDtoINTERFACE[self.dst_network_id][0])
                    ret += ('\nset service ' + self.servicename.upper())
                    ret += ('\nset schedule always')
                    ret += ('\nnext')
                    count = count + 1
                else:
                    ret += ('\nset dstintf ') + 'FW-OUT-' + current_vdom.upper()
                    ret += ('\nset service ' + self.servicename.upper())
                    ret += ('\nset schedule always')
                    ret += ('\nnext')
                    count = count + 1
            else:
                count = count + 1
                pass
        return ret
    
    def ipv4_host_or_network(self):
        src = ''
        dst = ''
        src_ipv4_host = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', self.from_ipv4))    
        dst_ipv4_host = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', self.to_ipv4))
        src_ipv4_net = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/', self.from_ipv4))
        dst_ipv4_net = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/', self.to_ipv4))
        if src_ipv4_host:
            src = 'host'
        if dst_ipv4_host:
            dst = 'host'
        if src_ipv4_net:
            src = 'net'
        if dst_ipv4_net:
            dst = 'net'
        return(src, dst)


    def ipv6_host_or_network(self):
        src_ipv6_host = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', self.from_ipv4))    
        dst_ipv6_host = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', self.to_ipv4))
        src_ipv6_net = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/', self.from_ipv4))
        dst_ipv6_net = bool(re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/', self.to_ipv4))
        if src_ipv6_host:
            src = 'host'
        if dst_ipv6_host:
            dst = 'host'
        if src_ipv6_net:
            src = 'net'
        if dst_ipv6_net:
            dst = 'net'
        return(src, dst)
        
    def dumpconfig_post(self):
            print('end\nend')

    @staticmethod
    def getList(conn):
        c = conn.cursor()
        c.execute('DROP VIEW IF EXISTS node_any_forti;')
        c.execute('CREATE VIEW node_any_forti AS SELECT host.node_id, host.name, host.ipv4_addr_txt AS ipv4_txt, host.ipv6_addr_txt AS ipv6_txt, n.terminator AS network_terminator, n.node_id AS network_id FROM host JOIN network n ON host.network_id = n.node_id UNION SELECT node_id, name, ipv4_txt, ipv6_txt, terminator AS network_terminator, node_id AS network_id FROM network;')
        c.execute('DROP VIEW IF EXISTS firewall_rule_ip_level_forti;')
        c.execute('CREATE VIEW firewall_rule_ip_level_forti AS SELECT fw.id, fw.is_ipv4, fw.is_ipv6, n.short_name, n.ipv4_gateway_txt, n.ipv6_gateway_txt, f.name AS from_node_name, f.ipv4_txt AS from_ipv4, f.ipv6_txt AS from_ipv6, t.name AS to_node_name, t.ipv4_txt AS to_ipv4, t.ipv6_txt AS to_ipv6, fl.name AS flow_name, s.name AS service_name, s.description AS service_description, s.dst_ports AS service_dst_ports, s.src_ports AS service_src_ports, f.network_id AS src_network_id, t.network_id AS dst_network_id, fw.id FROM network n, node_any_forti f, node_any_forti t, service s, firewall_rule fw, flow fl WHERE s.id = fw.service_id AND fl.id = fw.flow_id AND f.node_id = fw.from_node_id AND t.node_id = fw.to_node_id AND f.node_id = fw.from_node_id;')
        c.execute('''
SELECT
v.from_node_name,
v.from_ipv4,
v.from_ipv6,
v.to_node_name,
v.to_ipv4,
v.to_ipv6,
v.service_name,
srcn.terminator,
dstn.terminator,
v.src_network_id,
v.dst_network_id,
v.service_dst_ports,
v.service_src_ports,
v.is_ipv4,
v.is_ipv6,
v.flow_name,
v.short_name,
v.id
FROM firewall_rule_ip_level_forti v
join network srcn on v.src_network_id = srcn.node_id
join network dstn on v.dst_network_id = dstn.node_id
group by v.id
''')
        
        list = []
        for data in c.fetchall():
            list.append(Policy(data))
        return list
