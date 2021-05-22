from datetime import timedelta, datetime


class DataCache(object):
    def __init__(self, defaultExpireTime = timedelta(minutes=10), dbg=True):
        self.defaultExpireTime = defaultExpireTime

        self.cache = {}
        self.dbg = dbg

        self.processExpires = True

    def setProcessExpires(self, b):
        self.processExpires = b

    def __getitem__(self, key):
        c = self.cache[key]

        n = datetime.now()
        if (n - c['timestamp']) < c['expireTime'] or not self.processExpires:
            return c['data']

        del self.cache[key]

        if self.dbg:
            return

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __setitem__(self, key, val):
        self.cache[key] = {
            'data': val,
            'timestamp': datetime.now(),
            'expireTime': self.defaultExpireTime,
        }

    def items(self):
        keys = list(self.cache)
        for k in keys:
            try:
                val = self[k]
                yield (k, val)
            except:
                pass

    def get(self, key, default="", expired=""):
        try:
            return self[key]
        except KeyError:
            if default == "": return None
            return default

    def set(self, key, val, expireTime=None):
        if expireTime is None:
            expireTime = self.defaultExpireTime

        self.cache[key] = {
            'data': val,
            'timestamp': datetime.now(),
            'expireTime': expireTime,
        }

    def tryremove(self, key):
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    #the following you can call without triggering any expirations
    def getTotalExpireTime(self, key):
        """Get the total amount of time the key will be in the cache for"""
        c = self.cache[key]
        return c['expireTime']

    def getExpirationTime(self, key):
        """Return the datetime when the given key will expire"""
        c = self.cache[key]
        return c['timestamp'] + c['expireTime']

    def getTimeRemaining(self, key):
        """Get the time left until the item will expire"""
        return self.getExpirationTime(key) - datetime.now()

    def getTimestamp(self, key):
        return self.cache[key]['timestamp']

    def __len__(self):
        return len(self.cache)