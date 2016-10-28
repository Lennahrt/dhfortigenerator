import sqlite3
import os
import argparse
from components.Interface import *
from components.Vdom import *
from components.Service import *
from components.Network import *
from components.Host import *
from components.Route import *
from components.Policy import *

ap = argparse.ArgumentParser()
ap.add_argument('-a', action='store_true', help='Generate full configuration')
ap.add_argument('-i', action='store_true', help='Generate interface configuration')
ap.add_argument('-p', action='store_true', help='Generate ipv4 policy configuration')
ap.add_argument('-r', action='store_true', help='Generate static route configuration')
ap.add_argument('-r6', action='store_true', help='Generate static route configuration')
ap.add_argument('-s', action='store_true', help='Generate service object configuration')
ap.add_argument('-v', action='store_true', help='Generate vdom configuration')
ap.add_argument('-p6', action='store_true', help='Generate ipv6 policy configuration')
ap.add_argument('-n', action='store_true', help='Generate ipv4 network objects')
ap.add_argument('-n6', action='store_true', help='Generate ipv6 network objects')
ap.add_argument('-h4', action='store_true', help='Generate ipv4 host configuration')
ap.add_argument('-h6', action='store_true', help='Generate ipv6 host ocnfiguration')


args = ap.parse_args()

#os.system('rm db/ipplan.db.xr')
#os.system('unxz db/ipplan.db.xz')


conn = sqlite3.connect('db/ipplan.db')

interfaceList = Interface.getList(conn)
networkList = Network.getList(conn, interfaceList)

VDOM_IN_OUT_INTERFACES = Network.VDOM_IN_OUT_INTERFACES(networkList)
NID_VDOM, outside_network_ids = Network.NID_VDOM(networkList)
NIDtoINTERFACE = Network.NIDtoINTERFACE(networkList)
IFACEtoVDOM = Interface.IFACEtoVDOM(interfaceList)


vdomList = Vdom.getList(conn)
hostList = Host.getList(conn)
routeList = Route.getList(conn)
policyList = Policy.getList(conn)


print(outside_network_ids)

##### CREATE VDOMS #####

if args.v or args.a:
    conf = 'config vdom'
    for oneVdom in vdomList:
        conf += oneVdom.dumpconfig_pre()
        conf += 'next'
    print(conf + '\nend')

##### CREATE INTERFACES #####

if args.i or args.a:
    print('config global' + '\nconfig system interface')
    for oneInterface in Interface.getList(conn):
        print(oneInterface.dumpconfig())
    print('end\nend\n')


##### CREATE SERVICES #####

if args.s or args.a:
    for oneVdom in vdomList:
        conf = 'config vdom'
        conf += oneVdom.dumpconfig_pre()
        conf += 'configure firewall service custom\n'
        for oneService in Service.getList(conn):
            conf += oneService.dumpconfig()
        conf += oneVdom.dumpconfig_post() 
        print(conf)


##### CREATE FIREWALL IPV4_NETWORK OBJECTS #####


if args.n or args.a:
    conf = ''
    for oneVdom in vdomList:
        vdomNetworkList = oneVdom.getMyNetworks(networkList)
        conf += 'config vdom'
        conf += oneVdom.dumpconfig_pre()
        conf += 'configure firewall address\n'
        for network in vdomNetworkList:
            conf += network.ipv4_network_dumpconfig()
    conf += oneVdom.dumpconfig_post()
    print(conf)

##### CREATE FIREWALL IPV6_NETWORK OBJECTS #####

if args.n6 or args.a:
    conf = ''
    for oneVdom in vdomList:
        vdomNetworkList = oneVdom.getMyNetworks(networkList)
        conf += 'config vdom'
        conf += oneVdom.dumpconfig_pre()
        conf += 'configure firewall address'
        for network in vdomNetworkList:
            conf += network.ipv6_network_dumpconfig()
    print(conf)

##### CREATE FIREWALL IPV4_HOST OBJECTS #####


if args.h4 or args.a:
    conf = ''   
    for oneVdom in vdomList:
        conf += '\nconfig vdom'
        conf += oneVdom.dumpconfig_pre()
        conf += 'configure firewall address\n'
        for host in hostList:
            try:
                NID = NID_VDOM[host.network_id]
                if NID == oneVdom.name:
                    conf += host.dumpconfig_ipv4()
            except KeyError:
                if host.network_id in outside_network_ids:
                    conf += host.dumpconfig_ipv4()
                else:
                    continue
        conf += host.dumpconfig_post_ipv4()
    print(conf)

##### CREATE FIREWALL IPV6_HOST OBJECTS #####

if args.h6 or args.a:
    conf = ''
    for oneVdom in vdomList:
        conf += '\nconfig vdom'
        conf += oneVdom.dumpconfig_pre()
        conf += 'configure firewall address6\n'
        for host in hostList:
            try:
                NID = NID_VDOM[host.network_id]
                if NID == oneVdom.name:
                    conf += host.dumpconfig_ipv6()
            except KeyError:
                if host.network_id in outside_network_ids:
                    conf += host.dumpconfig_ipv6()
                else:
                    continue
        conf += host.dumpconfig_post_ipv6()
    print(conf)


##### CREATE FIREWALL IPV4_ROUTES #####

if args.r or args.a:
    conf = ''
    for oneVdom in vdomList:
        vdomRouteList = oneVdom.getMyRoutes(routeList)
        conf += 'config vdom'
        conf += oneVdom.dumpconfig_pre()
        conf += 'configure router static\n'
        for route in vdomRouteList:
            conf += route.ipv4_route_dumpconfig()
            #conf += route.ipv4_route_dumpdeviceconfig()
        conf += route.dumpconfig_post()
    print(conf)

##### CREATE FIREWALL IPV6_ROUTES #####

if args.r6 or args.a:
    conf = ''
    for oneVdom in vdomList:
        vdomRouteList = oneVdom.getMyRoutes(routeList)
        conf += 'config vdom'
        conf += oneVdom.dumpconfig_pre()
        conf += 'configure router static\n'
        for route in vdomRouteList:
            conf += route.ipv6_route_dumpconfig()
        conf += route.dumpconfig_post()
    print(conf)

##### CREATE IPV4 POLICY RULES #####

if args.p or args.a:
    current_policy_id = 0
    for oneVdom in vdomList:
        current_vdom = oneVdom.current_vdom()
        print('config vdom')
        print('edit vdom ' + current_vdom)
        print('configure firewall policy')
        for policy in policyList:
            src, dst = policy.ipv4_host_or_network()
            if policy.unrelatedtraffic1 == True:
                current_policy_id = policy.current_firewall_rule()
            elif policy.unrelatedtraffic2 ==True:
                current_policy_id = policy.current_firewall_rule()
            elif current_policy_id == policy.current_firewall_rule():
                pass
            else:
                cont, conf, any_host = policy.set_srcaddr(NID_VDOM, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src)
                if cont == 'src':
                    conf += policy.set_srcintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_dstaddr(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont, dst)
                    conf += policy.set_dstintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_service()
                    conf += policy.set_schedule()
                    print(conf)
                    current_policy_id = policy.current_firewall_rule()
                elif cont == 'dst':
                    conf += policy.set_srcintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_dstaddr(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont, dst)
                    conf += policy.set_dstintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_service()
                    conf += policy.set_schedule()
                    current_policy_id = policy.current_firewall_rule()
                    print(conf)
                elif any_host == True and current_vdom == 'dreamhack':
                    conf += policy.create_any_rule(IFACEtoVDOM, current_vdom, NIDtoINTERFACE, dst)
                    print(conf)
                else:
                    continue
        policy.dumpconfig_post()

##### CREATE IPV6 POLICY RULES #####

if args.p6 or args.a:
    current_policy_id = 0
    for oneVdom in vdomList:
        current_vdom = oneVdom.current_vdom()
        print('config vdom')
        print('edit vdom ' + current_vdom)
        print('configure firewall policy')
        for policy in policyList:
            src, dst = policy.ipv4_host_or_network()
            if policy.unrelatedtraffic1 == True:
                current_policy_id = policy.current_firewall_rule()
            elif policy.unrelatedtraffic2 ==True:
                current_policy_id = policy.current_firewall_rule()
            elif current_policy_id == policy.current_firewall_rule():
                pass
            else:
                cont, conf, any_host = policy.set_ipv6_srcaddr(NID_VDOM, NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, src)
                if cont == 'src':
                    conf += policy.set_srcintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_ipv6_dstaddr(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont, dst)
                    conf += policy.set_dstintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_service()
                    conf += policy.set_schedule()
                    print(conf)
                    current_policy_id = policy.current_firewall_rule()
                elif cont == 'dst':
                    conf += policy.set_srcintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_ipv6_dstaddr(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont, dst)
                    conf += policy.set_dstintf(NIDtoINTERFACE, VDOM_IN_OUT_INTERFACES, current_vdom, cont)
                    conf += policy.set_service()
                    conf += policy.set_schedule()
                    current_policy_id = policy.current_firewall_rule()
                    print(conf)
                elif any_host == True and current_vdom == 'dreamhack':
                    conf += policy.create_any_ipv6_rule(IFACEtoVDOM, current_vdom, NIDtoINTERFACE, dst)
                    print(conf)
                else:
                    continue
        policy.dumpconfig_post()

#print(conf)
##### CREATE FIREWALL IPV4_POLICIES ##### 
##### CREATE FIREWALL IPV6_POLICIES #####
conn.close()


