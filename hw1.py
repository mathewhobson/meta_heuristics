import sys
from itertools import permutations
import logging
import itertools

# global variables
global PATH
PATH = "input/" # folder path
machines = 5 # number of machines
jobs = 20 # number of jobs
job_machine_combinations=[(20,5), (20, 10), (20,20),(50, 5), (50, 10), (50, 20), (100, 5), (100, 10), (100, 20)]
num_interations = 20

# set logging
debug_mode = False  # Assume this might be set based on some condition or configuration
if debug_mode:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


# load file and build table
def load(machines, jobs):
    filename = PATH + "tai" + str(jobs) + "_" + str(machines) + "_1.txt"
    try:
        f = open(filename, "r")
    except:
        logging.error("File not found")
        exit(1)
    f.readline() # read line 1
    t = []
    for l in f.readlines():
        t += [list(map(int, l.split()))]
    logging.info(f'loaded {filename}')
    return t

# calculate makespan : input job_ids, output makespan
def cal_makespan(machines,job_order,job_duration):
    ms = [0] * machines
    for j_id in job_order:
        logging.debug(f'calculating job={j_id}')
        for m_id in range(machines):
            job_start_time = 0 if m_id == 0 else ms[m_id-1]
            job_start_time = max(job_start_time, ms[m_id])
            ms[m_id] = job_start_time + job_duration[m_id][j_id] # update makespan
            logging.debug(f'\t {ms[m_id]}')
    return ms[machines-1] #returns makespan for the last machine

def generate_permutations(jobs):
    for new_order in itertools.permutations(jobs):
        yield new_order

# greedy algorithm is very slow
def greedy(machines,jobs,job_duration):
    minimum_ms, maxiumum_ms, average_ms = 0
    original_job_order = list(range(jobs))
    ans_makespan = cal_makespan(machines,original_job_order,job_duration)
    print('baseline makespan {ans_makespan}')
    for new_order in generate_permutations(list(range(jobs))):
        makespan = cal_makespan(machines,new_order,job_duration)
        if makespan < ans_makespan:
            ans_jobs = new_order
            ans_makespan = makespan
            print(f'better job order found with duration {ans_makespan}')
            print(f'job combination={ans_jobs}')
    return  minimum_ms, maxiumum_ms, average_ms


# New Tabu Search function
def tabu_search(machines, jobs, job_duration, num_iterations=20):
    best_solution = list(range(jobs))
    best_makespan = cal_makespan(machines, best_solution, job_duration)
    tabu_list = [best_solution]
    makespans = [best_makespan]

    for _ in range(num_iterations):
        neighbors = []
        # Generate neighbors by swapping two jobs
        for i in range(jobs):
            for j in range(i + 1, jobs):
                new_solution = best_solution.copy()
                new_solution[i], new_solution[j] = new_solution[j], new_solution[i]
                if new_solution not in tabu_list:
                    neighbors.append(new_solution)

        # Evaluate neighbors
        current_best_makespan = float('inf')
        current_best_solution = None
        for neighbor in neighbors:
            makespan = cal_makespan(machines, neighbor, job_duration)
            if makespan < current_best_makespan:
                current_best_makespan = makespan
                current_best_solution = neighbor

        # Update if a better solution is found
        if current_best_makespan < best_makespan:
            best_makespan = current_best_makespan
            best_solution = current_best_solution
            tabu_list.append(best_solution)
            if len(tabu_list) > 10:  # Limit tabu list size
                tabu_list.pop(0)

        makespans.append(best_makespan)

    # Calculate statistics
    min_makespan = min(makespans)
    max_makespan = max(makespans)
    avg_makespan = sum(makespans) / len(makespans)

    return min_makespan, max_makespan, avg_makespan

if __name__ == "__main__":
    if len(sys.argv) == 3: # input numbers yourself, such as "python hw1.py 20 5"
        jobs = int(sys.argv[1])
        machines = int(sys.argv[2])
    job_duration = load(machines,jobs)
    job_order = list(range(jobs))
    logging.debug(f'job extracted from file={job_duration}')
    makespan = cal_makespan(machines,job_order,job_duration)

    makespans = list()
    for jobs,machines in job_machine_combinations:
        logging.info(f'Processing job={jobs}, machines={machines}')
        job_duration = load(machines, jobs)
        min_ms, max_ms, avg_ms = tabu_search(machines, jobs, job_duration, num_iterations=20)
        makespans.append((f'{jobs}x{machines}', 'Tabu Search', min_ms, max_ms, avg_ms))

    for makespan in makespans:
        print(makespan)