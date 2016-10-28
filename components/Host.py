import re
#from components.Utils import *

class Host(object):

    def __init__(self,data):
        self.name = data[0]
        self.ipv4address = data[1]
        self.ipv6address = data[2]
        self.network_id = data[3]

    def dumpconfig_ipv4(self):
        ret = '\nedit ' + self.name + '_' + self.ipv4address
        ret += '\nset subnet ' + self.ipv4address
        ret += '\nnext'
        return ret

    def dumpconfig_ipv6(self):
        ret6 = 'edit ' + self.name + '_' + self.ipv6address
        ret6 += '\nset ip6 ' + self.ipv6address
        ret6 += '\n'
        return ret6

    def dumpconfig_post_ipv4(self):
        ret = '\nend\nend'   
        return ret

    def dumpconfig_post_ipv6(self):
        ret6 = 'end\nend'
        return ret6

    @staticmethod
    def getList(conn):
        c = conn.cursor()
        c.execute('''
SELECT
host.name,
host.ipv4_addr_txt,
host.ipv6_addr_txt,
host.network_id
FROM
host;
''')
        list = []
        for data in c.fetchall():
            list.append(Host(data))
        return list








