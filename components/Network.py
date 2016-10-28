import re


class Network(object):

    def __init__(self,data):
        self.vdom = data[0]
        self.id = data[1]
        self.name = data[2]
        self.short_name = data[3]
        self.vlan = data[4]
        self.terminator = data[5]
        self.ipv4address = data[6]
        self.ipv6address = data[7]
        self.ipv4netmask = data[8]
        self.ipv6netmask = data[9]
        self.ipv4gateway = data[10]
        self.ipv6gateway = data[11]
        self.ipv6capable = data[12]
        self.located_on_dreamhack = self.name.startswith('EVENT@')
        self.is_link_net = self.short_name.startswith('FW-IN-')
        self.outside_interface = self.short_name.startswith('FW-OUT-')
        self.is_outside_nw = not((self.terminator != 'D-ASR-V' or 'D-FW-V') and self.name.startswith('EVENT@'))

            
    def get_value(self):
        lol = network_id_relates_to_internet
        return lol
            
            
    def ipv4_network_dumpconfig(self):
        ret = 'edit ' + self.short_name + '_IPV4_NET'
        ret += '\nset subnet ' + self.ipv4address
        ret += '\nnext\n'
        return ret

    def ipv4_host_dumpconfig(self):
        ret = '\nedit ' + self.short_name + '_' + self.ipv4address
        ret += '\nset subnet ' + self.ipv4address
        ret += '\nnext'
        return ret

    def ipv6_network_dumpconfig(self):
        try:
            ret = '\nedit ' + self.short_name + '_IPV6_NET'
            ret += '\nset ip6 ' + self.ipv6address
            ret += '\nnext'
        except:
	        TypeError
	        ret = ''
        return ret

    def ipv6_host_dumpconfig(self):
        ret = '\nedit ' + self.short_name + '_' + self.ipv6address
        ret += '\nset ip6 ' + self.ipv6address
        ret += '\nnext'
        return ret

    @staticmethod
    def NIDtoINTERFACE(networkList):
        NIDtoINTERFACE = {}
        for entry in networkList:
            if entry.vdom != '':
                if entry.vdom == 'mgmt':
                    NIDtoINTERFACE.setdefault(entry.id, ['FW-IN-CORE-MGMT', entry.vdom.upper()])
                elif entry.is_link_net:
                    NIDtoINTERFACE.setdefault(entry.id, ['FW-IN-' + entry.vdom.upper(), entry.vdom.upper()])
                elif entry.outside_interface:
                    NIDtoINTERFACE.setdefault(entry.id, ['FW-OUT-' + entry.vdom.upper(), 'None'])
                else:
                    NIDtoINTERFACE.setdefault(entry.id, [entry.short_name, entry.vdom.upper()])
            elif entry.short_name.startswith('CORE-LOOPBACKS'):
                NIDtoINTERFACE.setdefault(entry.id, ['FW-IN-CORE-MGMT', 'DREAMHACK'])
            else:
		continue
        return NIDtoINTERFACE

	

    @staticmethod
    def NID_VDOM(networkList):
        NID_VDOM = {}
        outside_network_ids = []
        for entry in networkList:
            if entry.vdom != '':
                if entry.vdom == 'mgmt':
                    NID_VDOM[entry.id] = 'dreamhack'
                else:
                    NID_VDOM[entry.id] = entry.vdom
            elif entry.terminator not in ('D-ASR-V', 'D-FW-V'):
                outside_network_ids.append(entry.id) 
            else:
                continue
        return(NID_VDOM, outside_network_ids)

    def get_host_interface(self, hostList):
        host_in_network = {}
        for entry in hostList:
            host_in_network[entry.network_id] = self.short_name
        return host_in_network
        
    @staticmethod
    def VDOM_IN_OUT_INTERFACES(networkList): #Retrieves FW-IN and FW-OUT interface for each VDOM as a dictionary. 
        values = {}
	for entry in networkList:
	    if entry.is_link_net:
	        values['FW-IN-' + entry.vdom] = entry.short_name
	    elif entry.outside_interface:
	        values['FW-OUT-' + entry.vdom] = entry.short_name
	    else:
	        continue
        return values
	    
    @staticmethod
    def getList(conn,interfaceList):
        c = conn.cursor()
        conn.text_factory = str
        c.execute('''
select distinct
case when iv.vrf_vdom = 'vrf' THEN
replace(iv.value,'prod','production')
ELSE
iv.value
end
,iv.network_id
,iv.name
,iv.short_name
,iv.vlan
,iv.terminator
,iv.ipv4_txt
,iv.ipv6_txt
,iv.ipv4_netmask_txt
,iv.ipv6_netmask_txt
,iv.ipv4_gateway_txt
,iv.ipv6_gateway_txt
,iv.ipv6_capable
from(
select
opt.value
,opt.name vrf_vdom
,nw.node_id network_id
,nw.name
,nw.short_name
,nw.vlan
,nw.terminator
,nw.ipv4_txt
,nw.ipv6_txt
,nw.ipv4_netmask_txt
,nw.ipv6_netmask_txt
,nw.ipv4_gateway_txt
,nw.ipv6_gateway_txt
,nw.ipv6_capable
from option opt
join network nw on nw.node_id = opt.node_id and opt.name in ('vdom', 'vrf')
UNION
select
''
,'' vrf_vdom
,nw.node_id network_id
,nw.name
,nw.short_name
,nw.vlan
,nw.terminator
,nw.ipv4_txt
,nw.ipv6_txt
,nw.ipv4_netmask_txt
,nw.ipv6_netmask_txt
,nw.ipv4_gateway_txt
,nw.ipv6_gateway_txt
,nw.ipv6_capable
from network nw
) iv
group by network_id
''')
        list = []
        for data in c.fetchall():
            list.append(Network(data))
	return list
