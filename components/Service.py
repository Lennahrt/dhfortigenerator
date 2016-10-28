import re

class Service(object):

    def __init__(self,data):
        self.name = data[0]
        self.raw_dst_portdata = data[1]
        self.raw_src_portdata = data[2]

        get_dst_tcp_udp_portdata = Service.calculate_dst_tcp_udp_range(self.raw_dst_portdata)
        self.dst_tcp_portdata = get_dst_tcp_udp_portdata[0]
        self.dst_udp_portdata = get_dst_tcp_udp_portdata[1]

    def dumpconfig(self):
        ret = 'edit ' + self.name
        if len(self.dst_tcp_portdata) > 0:
            ret += '\nset tcp-portrange ' + self.dst_tcp_portdata
        if len(self.dst_udp_portdata) > 0:
            ret += '\nset udp-portrange ' + self.dst_udp_portdata
        ret += '\nnext\n'
        return ret

    @staticmethod
    def calculate_dst_tcp_udp_range(raw_dst_data):
        tcp_ports = ''
        udp_ports = ''
        if raw_dst_data.find(',') is not -1:
            #print('*****OVER******' + raw_dst_data)
            split = re.split(',', raw_dst_data)
            for tcp_udp in split:
                splitvalue = re.search('(.{1,12})\/(.*)', tcp_udp)
                port = splitvalue.group(1)
                tcp_or_udp = splitvalue.group(2)
                if tcp_or_udp == 'tcp':
                    tcp_ports += port + " "
                elif tcp_or_udp == 'udp':
                    udp_ports += port + " "
        else:
            #print('*****UNDER******' + raw_dst_data)
            splitvalue = re.search('(.{1,12})\/(.*)', raw_dst_data)
            port = splitvalue.group(1)
            tcp_or_udp = splitvalue.group(2)
            if tcp_or_udp == 'tcp':
                tcp_ports += port + " "
            elif tcp_or_udp == 'udp':
                udp_ports += port + " "

        return(tcp_ports, udp_ports)


    @staticmethod
    def getList(conn):
        c = conn.cursor()
        c.execute('''
select name, dst_ports, src_ports from service
''')
        list = []
        for data in c.fetchall():
            list.append(Service(data))
        return list
