import re


class Route(object):

    def __init__(self,data):
        self.vdom = data[0]
        self.network_id = data[1]
        self.name = data[2]
        self.terminator = data[3]
        self.ipv4_network = data[4]
        self.ipv6_network = data[5]
        self.ipv4_netmask = data[6]
        self.ipv6_netmask = data[7]
        self.ipv4_gateway = data[8]
        self.ipv6_gateway = data[9]

    def dumpconfig_post(self):
        ret = 'end'
        ret += '\nend'
        return ret

    def ipv4_route_dumpconfig(self):
        ret = 'edit 0' 
        ret += '\nset gateway ' + self.ipv4_gateway
        ret += '\nset dst ' + self.ipv4_network
        ret += '\nset device ' + self.name
        ret += '\nnext\n'
        return ret 

    def ipv6_route_dumpconfig(self):
        ret = 'edit 0' 
        ret += '\nset gateway ' + self.ipv6_gateway
        ret += '\nset dst ' + self.ipv6_network
        ret += '\nset device ' + self.name
        ret += '\nnext\n'
        return ret

    @staticmethod
    def getList(conn):
        c = conn.cursor()
        c.execute('''
select distinct
case when iv.vrf_vdom = 'vrf' THEN
replace(replace(iv.value,'mgmt','dreamhack'),'prod','production')
ELSE
iv.value
end
,iv.network_id
,iv.short_name
,iv.terminator
,iv.ipv4_txt
,iv.ipv6_txt
,iv.ipv4_netmask_txt
,iv.ipv6_netmask_txt
,iv.ipv4_gateway_txt
,iv.ipv6_gateway_txt
from(
select
opt.value
,opt.name vrf_vdom
,nw.node_id network_id
,nw.short_name
,nw.terminator
,nw.ipv4_txt
,nw.ipv6_txt
,nw.ipv4_netmask_txt
,nw.ipv6_netmask_txt
,nw.ipv4_gateway_txt
,nw.ipv6_gateway_txt
from option opt
join network nw on nw.node_id = opt.node_id and opt.name in ('vrf', 'vdom') where terminator='D-ASR-V'
) iv
''')
        list = []
        for data in c.fetchall():
            list.append(Route(data))
        return list
