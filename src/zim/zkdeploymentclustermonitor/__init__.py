
from zim.zkdeploymentclustermonitor.basemonitor import IBaseMonitor, BaseMonitor
import time
import zc.zk
import zookeeper

def probe():
    return [Monitor()]

class Monitor(BaseMonitor):
    'Monitor ZooKeeper /hosts for convergence'

    name = __name__
    url = '/' + __name__
    interval = 300

    def __init__(self):
        pass

    def describe(self):
        return [self.url]

    def process(self, cb):
        try:
            zk = self.zk
        except AttributeError:
            try:
                self.zk = zc.zk.ZK('zookeeper:2181')
            except zookeeper.ZooKeeperException:
                return self.error(cb, self.url, "Can't connect to ZooKeeper")
            zk = self.zk

        try:
            hosts = zk.get_properties('/hosts')
        except zookeeper.NoNodeException:
            return self.error(cb, self.url, "No node: /hosts")

        if 'version' not in hosts:
            return self.error(cb, self.url, "No version: /hosts")

        now = time.time()
        version = hosts['version']
        if version != getattr(self, 'version', self):
            self.version = version
            self.version_time = now
            self.version_times = {}

        times = self.version_times
        late = []

        for name in zk.get_children('/hosts'):
            properties = zk.get_properties('/hosts/'+name)
            if 'version' in properties:
                name = properties.get('name', name)
                if properties['version'] == version:
                    if name in times:
                        del times[name]
                        if not times:
                            self.version_time = now
                    continue
                if name in times:
                    dur = int(now - times[name]) / 60
                else:
                    times[name] = now
                    dur = 0
                late.append((dur, name))

        if late:
            late.sort()
            dur, name = late[-1]
            mess = 'Unconverged (%s after %s minutes)' % (name, dur)
            if dur > 30:
                self.error(cb, self.url, mess)
            elif dur > 15:
                self.warn(cb, self.url, mess)
            else:
                self.ok(cb, self.url, mess)
        else:
            self.ok(cb, self.url, 'Converged (%s since %s)' % (
                version, time.ctime(self.version_time)))
