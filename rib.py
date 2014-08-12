import netaddr
import time
import datetime

from ryu.lib.dpid import dpid_to_str
from ryu.lib.port_no import port_no_to_str

class RoutingTable(dict):
    def update_entry(self, subnet, receive_port, neighbor_port=None, metric=0):
        try:
            r = self[subnet]
            r.receive_port = receive_port
            r.neighbor_port = neighbor_port
            r.metric = metric
            r.last_update = time.time()
        except KeyError:
            self[subnet] = RoutingEntry(receive_port, neighbor_port, metric)

    def update_by_neighbor(self, receive_port, neighbor_port, tbl):
        for subnet, entry in tbl.items():
            if subnet in self.keys():
                if entry.metric + 1 < self[subnet].metric:
                    self.update_entry(subnet, receive_port, neighbor_port, entry.metric + 1)
                else:
                    self[subnet].last_update = time.time()
            else:
                self.update_entry(subnet, receive_port, neighbor_port, entry.metric + 1)

class RoutingEntry(object):
    def __init__(self, receive_port, neighbor_port, metric=0):
        self.receive_port = receive_port
        self.neighbor_port = neighbor_port
        self.metric = metric
        self.last_update = time.time()
        self.flow_entry = None

    def to_dict(self):
        r = {}
        if self.receive_port.port_no:
            r['out_port'] = port_no_to_str(self.receive_port.port_no)
        if self.metric != 0:
            r['next_hop'] = dpid_to_str(self.neighbor_port.dpid)
        r['metric'] = self.metric
        r['last_update'] = datetime.datetime.fromtimestamp(self.last_update).strftime('%Y-%m-%d %H:%M:%S')
        r['flow_entry'] = self.flow_entry

        return r

    def to_flow_entry(self):
        return