import re

class Interface(object):

    def __init__(self,data):
        self.name = data[0]
        self.vdom = data[2]
        self.ipv4_network = data[3]
        self.alias = data[4]
        self.ipv6_network = data[5]
        self.vlan = data[6]
        self.terminator = data[7]
        self.node_id = data[8]

        self.is_outside = self.name.startswith('FW-OUT-')

        if self.terminator == 'D-FW-V':
            self.fw_ipv4_addr = Interface.add_to_octet_ipv4(self.ipv4_network,1)
            self.fw_ipv6_addr = Interface.add_to_octet_ipv6(self.ipv6_network,1)
        elif self.terminator == 'D-ASR-V':
            self.fw_ipv4_addr = Interface.add_to_octet_ipv4(self.ipv4_network,2)
            self.fw_ipv6_addr = Interface.add_to_octet_ipv6(self.ipv6_network,2)
        
        self.interface = "FW_LAG"
        self.networkList = []

	
    def dumpconfig(self):
        ret = 'edit ' + self.name
        ret += '\n set vdom ' + self.vdom
        ret += '\n set ip ' + self.fw_ipv4_addr
        ret += '\n set alias ' + self.alias
        ret += '\n set interface ' + self.interface
        ret += '\n set vlanid ' + str(self.vlan)
        ret += '\n set dhcp-relay-ip "77.80.231.201" "77.80.231.202" "77.80.231.213"'
        ret += '\n set config ipv6'
        ret += '\n set ip6-address ' + self.fw_ipv6_addr
        ret += '\nnext'
        return ret 
    
    @staticmethod
    def getList(conn):
        c = conn.cursor()
        c.execute('''
select
network.short_name,
option.name,
option.value,
network.ipv4_txt,
network.name,
network.ipv6_txt,
network.vlan,
network.terminator,
network.node_id
FROM option,network
WHERE option.node_id=network.node_id
and option.name="vdom"
and network.terminator in ("D-ASR-V","D-FW-V")
''')
        ifaceList = []
        for ifaceData in c.fetchall():
            ifaceList.append(Interface(ifaceData))
        return ifaceList
        
    @staticmethod
    def add_to_octet_ipv4(baseip,add):
        address_split = re.search('(\d+\.\d+\.\d+\.)(\d+)(.+)', baseip)
        return(address_split.group(1) + str(int(address_split.group(2)) + add) + address_split.group(3))

    @staticmethod
    def add_to_octet_ipv6(baseip,add):
        address_split = re.search('(.*::)(.*)', baseip)
        return(address_split.group(1) + str(add) + address_split.group(2))

    @staticmethod
    def IFACEtoVDOM(interfaceList):
	IFACEtoVDOM = {}
	count = 1
	for entry in interfaceList:
	    IFACEtoVDOM.setdefault(count, [entry.vdom.upper(), entry.name, entry.node_id])
	    count = count + 1
	return IFACEtoVDOM    
