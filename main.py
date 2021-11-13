import simulate as sim, random

class barajas_airport:
    def __init__(self,n):
        self.n = n
        self.oo = 1e18
        self.restore_data()

    def restore_data(self):
        self.current_time = 0
        self.next_arrival_time = self.oo

        self.started_landing_time = [self.oo for _ in range(self.n)]
        self.finished_landing_time = [self.oo for _ in range(self.n)]

        self.started_fueling_time = [self.oo for _ in range(self.n)]
        self.finished_fueling_time = [self.oo for _ in range(self.n)]

        self.started_loading_time = [self.oo for _ in range(self.n)]
        self.finished_loading_time = [self.oo for _ in range(self.n)]

        self.started_downloading_time = [self.oo for _ in range(self.n)]
        self.finished_downloading_time = [self.oo for _ in range(self.n)]

        self.finished_onfloor_time = [self.oo for _ in range(self.n)]

        self.started_repairing_time = [self.oo for _ in range(self.n)]
        self.finished_repairing_time = [self.oo for _ in range(self.n)]

        self.started_takingoff_time = [self.oo for _ in range(self.n)]
        self.departure_time = [self.oo for _ in range(self.n)]

        self.queue_size = 0

        self.occupied_time = [0 for _ in range(self.n)]
        self.airplane_arrival = []
        self.airplane_departure = []
        self.airplane_count = 0
        self.procesed_airplanes = 0
        self.plane_in_track = [-1 for _ in range(self.n)]
        self.running_events = [0 for _ in range(self.n)]

        self.logs = []

    def log(self, msg):
        minutes = round(self.current_time)
        hours = minutes // 60
        minutes = minutes % 60
        days = hours // 24
        hours = hours % 24
        self.logs.append(f'{days}d {hours}h {minutes}m: {msg}')
        #print(self.logs[-1])

    def get_free_track(self):
        available_tracks = [i for i in range(self.n) if
                            self.plane_in_track[i] == -1]
        if len(available_tracks) == 0: return -1
        return random.choice(available_tracks)

    def get_track(self, arr):
        mn = min(arr)
        return arr.index(mn)

    def generate_next_airplane_time(self, lam=1/20):
        return self.current_time + sim.exponential(lam)

    def generate_landing_time(self, mu=10, sigma2=5):
        return self.current_time + sim.normal(mu,sigma2)

    def generate_fueling_time(self, lam=1/30):
        return self.current_time + sim.exponential(lam)

    def generate_loading_time(self, lam=1/30):
        return self.current_time + sim.exponential(lam)

    def generate_downloading_time(self, lam=1/30):
        return self.current_time + sim.exponential(lam)

    def generate_repairing_time(self, lam=1/15):
        return self.current_time + sim.exponential(lam)

    def generate_takingoff_time(self, mu=10, sigma2=5):
        return self.current_time + sim.normal(mu,sigma2)

    def new_airplane_event(self):
        self.next_arrival_time = self.generate_next_airplane_time()

        self.airplane_arrival.append(0)
        self.airplane_departure.append(0)
        cur = self.airplane_count
        self.airplane_count += 1

        self.log(f'Airplane #{cur + 1} has arrived.')

        self.queue_size += 1
        if self.queue_size == 1:
            track = self.get_free_track()
            if track != -1:
                self.started_landing_time[track] = self.current_time
                self.airplane_arrival[self.procesed_airplanes] = self.current_time
                self.plane_in_track[track] = self.procesed_airplanes
                self.procesed_airplanes += 1
                self.queue_size -= 1
                return
        self.log(f'Airplane #{cur + 1} has been added to the queue.')


    def started_landing_event(self):
        track = self.get_track(self.started_landing_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started landing in track {track + 1}.')
        self.started_landing_time[track] = self.oo
        self.finished_landing_time[track] = self.generate_landing_time()

    def finished_landing_event(self):
        track = self.get_track(self.finished_landing_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'finished landing in track {track + 1}.')
        self.finished_landing_time[track] = self.oo
        self.started_fueling_time[track] = self.current_time

        self.running_events[track] += 1

        p = sim.uniform(0, 1)
        u = sim.uniform(0, 1)
        if u <= p:
            self.running_events[track] += 1
            self.started_loading_time[track] = self.current_time

        p = sim.uniform(0, 1)
        u = sim.uniform(0, 1)
        if u <= p:
            self.running_events[track] += 1
            self.started_downloading_time[track] = self.current_time


    def started_loading_event(self):
        track = self.get_track(self.started_loading_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started loading in track {track + 1}.')
        self.started_loading_time[track] = self.oo
        self.finished_loading_time[track] = self.generate_loading_time()

    def finished_loading_event(self):
        track = self.get_track(self.finished_loading_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'finished loading in track {track + 1}.')
        self.finished_loading_time[track] = self.oo

        self.running_events[track] -= 1
        if self.running_events[track] == 0:
            self.finished_onfloor_time[track] = self.current_time

    def started_downloading_event(self):
        track = self.get_track(self.started_downloading_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started downloading in track {track + 1}.')
        self.started_downloading_time[track] = self.oo
        self.finished_downloading_time[track] = self.generate_downloading_time()

    def finished_downloading_event(self):
        track = self.get_track(self.finished_downloading_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'finished downloading in track {track + 1}.')
        self.finished_downloading_time[track] = self.oo

        self.running_events[track] -= 1
        if self.running_events[track] == 0:
            self.finished_onfloor_time[track] = self.current_time

    def started_fueling_event(self):
        track = self.get_track(self.started_fueling_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started fueling in track {track + 1}.')
        self.started_fueling_time[track] = self.oo
        self.finished_fueling_time[track] = self.generate_fueling_time()

    def finished_fueling_event(self):
        track = self.get_track(self.finished_fueling_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'finished fueling in track {track + 1}.')
        self.finished_fueling_time[track] = self.oo

        self.running_events[track] -= 1
        if self.running_events[track] == 0:
            self.finished_onfloor_time[track] = self.current_time

    def finished_onfloor_event(self):
        track = self.get_track(self.finished_onfloor_time)
        self.finished_onfloor_time[track] = self.oo
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'finished on floor operations in track {track + 1}.')

        u = sim.uniform(0, 1)
        if u <= .1:
            self.started_repairing_time[track] = self.current_time
        else:
            self.started_takingoff_time[track] = self.current_time

    def started_repairing_event(self):
        track = self.get_track(self.started_repairing_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'has broken in track {track + 1}.')
        self.started_repairing_time[track] = self.oo
        self.finished_repairing_time[track] = self.generate_repairing_time()

    def finished_repairing_event(self):
        track = self.get_track(self.finished_repairing_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'finished repairing in track {track + 1}.')
        self.finished_repairing_time[track] = self.oo
        self.started_takingoff_time[track] = self.current_time

    def started_takingoff_event(self):
        track = self.get_track(self.started_takingoff_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started taking off in track {track + 1}.')
        self.started_takingoff_time[track] = self.oo
        self.departure_time[track] = self.generate_takingoff_time()

    def departure_event(self):
        track = self.get_track(self.departure_time)
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'has departured from track {track + 1}.')
        self.departure_time[track] = self.oo

        plane = self.plane_in_track[track]
        self.plane_in_track[track] = -1
        self.airplane_departure[plane] = self.current_time
        self.occupied_time[track] += self.airplane_departure[plane] \
                                     - self.airplane_arrival[plane]

        if self.queue_size > 0:
            self.started_landing_time[track] = self.current_time
            self.airplane_arrival[self.procesed_airplanes] = self.current_time
            self.plane_in_track[track] = self.procesed_airplanes
            self.procesed_airplanes += 1
            self.queue_size -= 1

    def simulate_barajas_airport(self, time):
        self.next_arrival_time = self.generate_next_airplane_time()

        while True:
            if self.next_arrival_time > time: self.next_arrival_time = self.oo

            tbx = min(self.started_landing_time)
            tcx = min(self.finished_landing_time)
            tdx = min(self.started_loading_time)
            tex = min(self.finished_loading_time)
            tfx = min(self.started_downloading_time)
            tgx = min(self.finished_downloading_time)
            thx = min(self.started_fueling_time)
            tix = min(self.finished_fueling_time)
            tjx = min(self.finished_onfloor_time)
            tkx = min(self.started_repairing_time)
            tlx = min(self.finished_repairing_time)
            tmx = min(self.started_takingoff_time)
            tnx = min(self.departure_time)

            mn = min([self.next_arrival_time,tbx,tcx,tdx,tex,
                      tfx,tgx,thx,tix,tjx,tkx,tlx,tmx,tnx])
            if mn >= self.oo: break
            self.current_time = mn

            if self.next_arrival_time == mn:  self.new_airplane_event()
            elif tbx == mn: self.started_landing_event()
            elif tcx == mn: self.finished_landing_event()
            elif tdx == mn: self.started_loading_event()
            elif tex == mn: self.finished_loading_event()
            elif tfx == mn: self.started_downloading_event()
            elif tgx == mn: self.finished_downloading_event()
            elif thx == mn: self.started_fueling_event()
            elif tix == mn: self.finished_fueling_event()
            elif tjx == mn: self.finished_onfloor_event()
            elif tkx == mn: self.started_repairing_event()
            elif tlx == mn: self.finished_repairing_event()
            elif tmx == mn: self.started_takingoff_event()
            elif tnx == mn: self.departure_event()

        self.logs.append('\n')
        self.logs.append(f'Planes processed: {self.airplane_count}')

        for i in range(self.n):
            self.logs.append(f'Track #{i + 1}: '
                             f'{round(self.current_time - self.occupied_time[i])} '
                             f'minutes empty.')

        return self.logs


ba = barajas_airport(5)

logs = ba.simulate_barajas_airport(7 * 24 * 60)
for i in logs: print(i)