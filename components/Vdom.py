import re


class Vdom(object):

    def __init__(self,data):
        self.name = data[0]
    
    def current_vdom(self):
	    ret = self.name
	    return ret
	
    def dumpconfig_pre(self):
        ret = '\nedit ' + self.name
        ret += '\n'
        return ret

    def dumpconfig_post(self):
        ret = 'end\nend'
        return ret

    def getOutsideNetworks(networkList):
        dict = {}
        for network in networkList:
            if (network.terminator != 'D-ASR-V' or 'D-FW-V') and network.name.startswith('EVENT@') == False:
                dict[network.id] = network.name
            else:
                continue
        return(dict)
    
    def getMyNetworks(self, networkList):
        list = []
        for network in networkList:
	    if network.vdom == self.name:
                list.append(network)
	    elif network.vdom == '':
		list.append(network)
	    elif network.vdom == 'mgmt' and self.name == 'dreamhack':
		list.append(network)
        return(list)

    def getMyRoutes(self, routeList):
        list = []
        for route in routeList:
            if route.vdom == self.name:
                list.append(route)
        return(list)


    @staticmethod
    def getList(conn):
        c = conn.cursor()
        c.execute('''
SELECT value FROM option where name="vdom" and value !="dreamhack-vpn" GROUP BY value
''')
        list = []
        for data in c.fetchall():
            list.append(Vdom(data))
        return list
