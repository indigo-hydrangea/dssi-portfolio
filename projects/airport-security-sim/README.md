# Airport Security Simulation (SimPy)
A discrete-event simulation of a two-stage airport security system, built in Python with SimPy.

## Problem
Simulate a simplified airport security process:
- Passenger arrivals follow a Poisson process with rate \u03bb = 5 per minute (mean interarrival time = 0.2 minutes).
- ID/boarding-pass check is a multi-server queue with **exponential** service time (mean 0.75 minutes).
- Passengers then join the **shortest** personal-check queue, where scan time is **uniform** between 0.5 and 1.0 minutes.

Goal: explore staffing levels to keep **average wait times below 15 minutes** (the busy-airport option uses \u03bb = 50/min).

## Solution
The simulation models:
- **ID check** as a single SimPy `Resource` with capacity = number of checkers.
- **Personal check** as multiple single-capacity resources (one per scanner).
- **Queue policy** that assigns each passenger to the shortest personal-check line.

The script runs multiple replications and reports **mean ID wait**, **mean personal wait**, and **total wait**. It currently sweeps the number of ID checkers, while personal-check lines are parameterized and can be swept similarly.

## Highlights
- Stochastic processes: Poisson arrivals, exponential and uniform service times.
- Discrete-event simulation and queueing logic in SimPy.
- Replication-based averaging for stable wait-time estimates.


Adjust these parameters at the top of the script to explore different scenarios:
- `PassInter` (interarrival time) to switch between normal and busy airport.
- `NumWorkers` and `NumPersonalLines` for staffing levels.

