import sqlite3
from components.Interface import *
from components.Vdom import *
from components.Service import *
from components.Network import *
from components.Host import *

conn = sqlite3.connect('db/ipplan.db')

networkList = Network.getList(conn)
vdomList = Vdom.getList(conn)
hostList = Host.getList(conn)
networkID_vdom = Network.key_networkID_vdom(networkList)

#####CREATE INTERFACES #####

conf = ''
for oneVdom in vdomList:
    conf += '\n\n************************************\n'
    conf += '\nconfig vdom'
    conf += oneVdom.dumpconfig_pre()
    conf += 'configure firewall address\n'
    for host in hostList:
        try:
            NID = networkID_vdom[host.network_id]
            if NID == oneVdom.name:
                conf += host.dumpconfig_ipv4()
        except KeyError:
                continue
print(conf)



#####CREATE INTERFACES #####

#for oneInterface in Interface.getList(conn):
#    print(oneInterface.dumpconfig())
#print('end\nend\n')


#####CREATE SERVICES #####

#for oneVdom in Vdom.getList(conn):
#    conf = 'config vdom'
#    conf += oneVdom.dumpconfig_pre()
#    conf += 'configure firewall service custom\n'
#    for oneService in Service.getList(conn):
#        conf += oneService.dumpconfig()
#    conf += oneVdom.dumpconfig_post() 
    #print(conf)


#####CREATE FIREWALL IPV4_NETWORK OBJECTS #####

#conf = ''
#
#for oneVdom in vdomList:
#    vdomNetworkList = oneVdom.getMyNetworks(networkList)
#    conf += '\n\n************************************\n'
#    conf += '\nconfig vdom'
#    conf += oneVdom.dumpconfig_pre()
#    conf += 'configure firewall address'
#    for network in vdomNetworkList:
#        conf += network.ipv4_network_dumpconfig()


#####CREATE FIREWALL IPV6_NETWORK OBJECTS #####

#conf = ''
#for oneVdom in vdomList:
#    vdomNetworkList = oneVdom.getMyNetworks(networkList)
#    conf += '\n\n************************************\n'
#    conf += '\nconfig vdom'
#    conf += oneVdom.dumpconfig_pre()
#    conf += 'configure firewall address'
#    for network in vdomNetworkList:
#        conf += network.ipv6_network_dumpconfig()


#####CREATE FIREWALL IPV4_HOST OBJECTS #####

#for oneVdom in vdomList:
#    vdomNetworkList = oneVdom.getMyNetworks(networkList)
#    vdomHostList = oneVdom.getMyHosts(hostList)
#    conf += '\n\n************************************\n'
#    conf += '\nconfig vdom'
#    conf += oneVdom.dumpconfig_pre()
#    conf += 'configure firewall address'
    #
    #print(vdomNetworkList)

#print(conf)

#####CREATE FIREWALL IPV6_HOST OBJECTS #####

#conf = ''
#hostList = Network.getList(conn)
#vdomList = Vdom.getList(conn)
#for oneVdom in vdomList:
#    vdomHostList = oneVdom.getMyHosts(hostList)
#    conf += '\n\n************************************\n'
#    conf += '\nconfig vdom'
#    conf += oneVdom.dumpconfig_pre()
#    conf += 'configure firewall address'
#    for host in vdomHostList:
#        conf += network.ipv6_host_dumpconfig()


    

#print(conf)
#for address in Addressobject.getHostList(conn):
#    x=""
#    print(address.name)
#        conf += address.dumpconfig_ipv4()
#        conf += address.dumpconfig_post_ipv4()
#        print(conf)
#print(conf)

"""
    conf = 'config vdom'
    conf += oneVdom.dumpconfig_pre()
    conf += 'configure firewall address\n'
    for address in Addressobject.getNetworkList(conn):
        conf += address.dumpconfig_network_ipv4()
        conf += address.dumpconfig_post_ipv4()
        print(conf)
   """     

#####CREATE FIREWALL IPV6_ADDRESS OBJECTS #####
#for oneVdom in Vdom.getList(conn):
#    conf = 'config vdom'
#    conf += oneVdom.dumpconfig_pre()
#    conf += 'configure firewall address6\n'
#    for address in Addressobject.getList(conn):
#        conf += address.dumpconfig_ipv6()
#        conf += address.dumpconfig_post_ipv6()





conn.close()


