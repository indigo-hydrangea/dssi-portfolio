
import itertools
import random

import simpy
import matplotlib.pyplot as plt

Rand_Seed= 28
NumWorkers = 5  # default number of ID/boarding-pass checkers
CheckTime = 0.75  # average minutes an ID checker spends per passenger
PassInter = 0.02  # average minutes between passenger arrivals (Poisson process)
SimTime = 480  # minutes to simulate (480 = 8-hour “day”)
NumPersonalLines = 4  # number of personal-check scanners
PersonalMin = 0.5  # minimum minutes for personal scan
PersonalMax = 1.0  # maximum minutes for personal scan

class Airport:
    """Airport security system with ID checkers and personal scanners."""

    def __init__(self, env, num_workers, check_time, num_personal, personal_min, personal_max):
        self.env = env
        self.server = simpy.Resource(env, num_workers)
        self.checktime = check_time
        # each scanner is modeled as its own resource with capacity 1
        self.personal_lines = [simpy.Resource(env, capacity=1) for _ in range(num_personal)]
        self.personal_time = (personal_min, personal_max)
        # keep simple lists of waits so we can average at the end
        self.id_wait_times = []
        self.personal_wait_times = []
        self.total_wait_times = []

    def check(self, passenger):
        """SimPy process: ID checker spends check_time minutes with this passenger."""
        yield self.env.timeout(self.checktime)



def passenger(env, name, ap):
    """Passenger process: wait for ID check, then head to shortest personal scanner."""
    arrival_time = env.now
    # wait for an ID checker to become free
    with ap.server.request() as request:
        yield request

        id_wait = env.now - arrival_time
        ap.id_wait_times.append(id_wait)
        yield env.process(ap.check(name))

    screen_arrival = env.now  # arrival time at the personal scanners
    # choose the scanner with the smallest (queue + in-service) count
    line = min(ap.personal_lines, key=lambda r: len(r.queue) + r.count)
    with line.request() as screen_request:
        yield screen_request
        personal_wait = env.now - screen_arrival
        ap.personal_wait_times.append(personal_wait)
        scan_time = random.uniform(*ap.personal_time)  # uniform(0.5, 1.0) minutes
        yield env.timeout(scan_time)

    ap.total_wait_times.append(id_wait + personal_wait)


def setup(env, num_workers, check_time, pass_inter, num_personal, personal_min, personal_max,
          initial_busy=True):
    """Create the airport resources, seed an initial batch, and keep generating passengers."""
    airport = Airport(env, num_workers, check_time, num_personal, personal_min, personal_max)
    env.airport = airport

    passenger_count = itertools.count()

    # Start with one passenger per ID checker so servers are busy but no queue forms
    initial_passengers = num_workers if initial_busy else 0
    for _ in range(initial_passengers):
        env.process(passenger(env, f'Passenger {next(passenger_count)}', airport))

    # Generate new passengers with exponential interarrival times
    while True:
        interarrival = random.expovariate(1 / pass_inter)
        yield env.timeout(interarrival)
        env.process(passenger(env, f'Passenger {next(passenger_count)}', airport))


def _run_once(num_workers, check_time, pass_inter, num_personal, personal_min, personal_max,
              sim_time, rand_seed, initial_busy=True):
    """Run a single replication of the security simulation."""
    if num_workers <= 0:
        raise ValueError("Number of workers must be positive for a simulation run.")

    random.seed(rand_seed)

    env = simpy.Environment()
    env.process(
        setup(
            env,
            num_workers,
            check_time,
            pass_inter,
            num_personal,
            personal_min,
            personal_max,
            initial_busy=initial_busy,
        )
    )

    env.run(until=sim_time)

    airport = getattr(env, "airport", None)
    if not airport or not airport.id_wait_times:
        return None

    mean_id_wait = sum(airport.id_wait_times) / len(airport.id_wait_times)
    mean_personal_wait = (sum(airport.personal_wait_times) / len(airport.personal_wait_times)
                          if airport.personal_wait_times else 0.0)
    mean_total_wait = (sum(airport.total_wait_times) / len(airport.total_wait_times)
                       if airport.total_wait_times else 0.0)

    return {
        "mean_id_wait": mean_id_wait,
        "mean_personal_wait": mean_personal_wait,
        "mean_total_wait": mean_total_wait,
    }


def RunSim(num_workers, replicates=5, check_time=CheckTime, pass_inter=PassInter,
           num_personal=NumPersonalLines, personal_min=PersonalMin, personal_max=PersonalMax,
           sim_time=SimTime, rand_seed=Rand_Seed, initial_busy=True):
    """Run several replications for one worker count and report mean waits."""
    replicate_stats = []
    for rep in range(replicates):
        seed = rand_seed + rep + num_workers * 1000
        stats = _run_once(
            num_workers,
            check_time,
            pass_inter,
            num_personal,
            personal_min,
            personal_max,
            sim_time,
            seed,
            initial_busy=initial_busy,
        )
        if stats:
            replicate_stats.append(stats)

    if not replicate_stats:
        print(f"Workers {num_workers:2d} | no completed passengers in replicates.")
        return None

    mean_stats = {
        key: sum(stat[key] for stat in replicate_stats) / len(replicate_stats)
        for key in replicate_stats[0]
    }
    print(
        f"Workers {num_workers:2d} | ID wait {mean_stats['mean_id_wait']:.2f} min | "
        f"Personal wait {mean_stats['mean_personal_wait']:.2f} min | "
        f"Total wait {mean_stats['mean_total_wait']:.2f} min"
    )
    return mean_stats


if __name__ == "__main__":
    print('Airport simulation summary')
    workers_tested = []
    id_waits = []
    personal_waits = []
    total_waits = []

    for workers in range(1, 41):
        stats = RunSim(workers)
        if stats:
            workers_tested.append(workers)
            id_waits.append(stats["mean_id_wait"])
            personal_waits.append(stats["mean_personal_wait"])
            total_waits.append(stats["mean_total_wait"])

    if workers_tested:
        plt.figure(figsize=(8, 5))
        plt.plot(workers_tested, id_waits, marker='o', label='ID wait')
        plt.plot(workers_tested, personal_waits, marker='s', label='Personal wait')
        plt.plot(workers_tested, total_waits, marker='^', label='Total wait')
        plt.xlabel('Number of ID workers')
        plt.ylabel('Mean wait (minutes)')
        plt.title('Mean waits by staffing level')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
