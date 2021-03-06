import time
import numpy as np

class Tracker:
    def __init__(self,name):
        self.name = name

class TimingTracker(Tracker):
    def __init__(self):
        self.t = np.nan
        Tracker.__init__(self,'Timer')

    def start(self):
        self.start = time.time()

    def get_elapsed(self):
        self.t = time.time() - self.start
        return self.t

class GPTracker(TimingTracker):
    def __init__(self,dim,npts):
        self.stats = {'dim':dim,'npts':npts,'optimization':False}
        self.models = []
        TimingTracker.__init__(self)
        self.start()
        
    def end(self):
        self.stats['t'] = self.get_elapsed()
        

        
        
