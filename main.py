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
        self.finished_loading_time = [self.oo for _ in range(self.n)]
        self.finished_repairing_time = [self.oo for _ in range(self.n)]
        self.departure_time = [self.oo for _ in range(self.n)]

        self.queue_size = 0

        self.occupied_time = [0 for _ in range(self.n)]
        self.airplane_arrival = []
        self.airplane_departure = []
        self.airplane_count = 0
        self.procesed_airplanes = 0
        self.plane_in_track = [-1 for _ in range(self.n)]

        self.logs = []

    def log(self, msg):
        self.logs.append(f'{round(self.current_time,2)}: {msg}')

    def get_free_track(self):
        available_tracks = [i for i in range(self.n) if
                            self.plane_in_track[i] == -1]
        if len(available_tracks) == 0: return -1
        return random.choice(available_tracks)

    def get_landing_track(self):
        mn = min(self.started_landing_time)
        return self.started_landing_time.index(mn)

    def get_loading_track(self):
        mn = min(self.finished_landing_time)
        return self.finished_landing_time.index(mn)

    def get_repairing_track(self):
        mn = min(self.finished_loading_time)
        return self.finished_loading_time.index(mn)

    def get_takingoff_track(self):
        mn = min(self.finished_repairing_time)
        return self.finished_repairing_time.index(mn)

    def get_finished_track(self):
        mn = min(self.departure_time)
        return self.departure_time.index(mn)

    def generate_next_airplane_time(self, lam=1/20):
        return self.current_time + sim.exponential(lam)

    def generate_landing_time(self, mu=10, sigma2=5):
        return self.current_time + sim.normal(mu,sigma2)

    def generate_loading_time(self, lam=1/30):
        return self.current_time + sim.exponential(lam)

    def generate_repairing_time(self, lam=1/15):
        return self.current_time + sim.exponential(lam)

    def generate_fueling_time(self, lam=1/30):
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


    def landing_airplane_event(self):
        track = self.get_landing_track()
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started landing in track {track + 1}.')
        self.started_landing_time[track] = self.oo
        self.finished_landing_time[track] = self.generate_landing_time()

    def loading_airplane_event(self):
        track = self.get_loading_track()
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started loading and fueling in track {track + 1}.')
        self.finished_landing_time[track] = self.oo
        self.finished_loading_time[track] = max(self.generate_loading_time(),
                             self.generate_fueling_time())

    def repairing_airplane_event(self):
        track = self.get_repairing_track()
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'finished loading and fueling in track {track + 1}.')
        self.finished_loading_time[track] = self.oo

        u = sim.uniform(0, 1)
        if u <= .1:
            self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                     f'has broken in track {track + 1}.')
            self.finished_repairing_time[track] = self.generate_repairing_time()
        else:
            self.finished_repairing_time[track] = self.current_time

    def takingoff_airplane_event(self):
        track = self.get_takingoff_track()
        self.log(f'Airplane #{self.plane_in_track[track] + 1} '
                 f'started taking off in track {track + 1}.')
        self.finished_repairing_time[track] = self.oo
        self.departure_time[track] = self.generate_takingoff_time()

    def finished_airplane_event(self):
        track = self.get_finished_track()
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
            tdx = min(self.finished_loading_time)
            tex = min(self.finished_repairing_time)
            tfx = min(self.departure_time)

            mn = min([self.next_arrival_time,tbx,tcx,tfx,tdx,tex])
            if mn >= self.oo: break
            self.current_time = mn

            if self.next_arrival_time == mn:  self.new_airplane_event()
            elif tbx == mn: self.landing_airplane_event()
            elif tcx == mn: self.loading_airplane_event()
            elif tdx == mn: self.repairing_airplane_event()
            elif tex == mn: self.takingoff_airplane_event()
            elif tfx == mn: self.finished_airplane_event()

        for i in range(self.n):
            self.logs.append(f'Track #{i + 1}: {self.current_time - self.occupied_time[i]}.')

        return self.logs


ba = barajas_airport(4)

logs = ba.simulate_barajas_airport(10080)
for i in logs: print(i)