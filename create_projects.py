import pandas as pd
import numpy as np

import itertools
import argparse
import os
import json


from SALib.sample import saltelli
from collections import defaultdict

aparser = argparse.ArgumentParser()
required_arguments = aparser.add_argument_group('required arguments')
required_arguments.add_argument('--output-dir', '-od',
                                help='a path to a suitable folder (ideally empty) where the new configurations will '
                                     'be stored', required=True)
required_arguments.add_argument('--ranges', '-r',
                                help='a csv file that determines the values to infer', required=True)
required_arguments.add_argument('--mode', '-m',
                                help='The mode in which the ranges file will be interpreted, this is either \'montecarlo\''
                                     ' or \'discrete\', defaults to montecarlo. When montecarlo is selected, the -n '
                                     'argument is mandatory', required=True, default='montecarlo', 
                                choices=['montecarlo', 'discrete', 'saltelli'])
required_arguments.add_argument('--num-simulations', '-n', 
                                help='number of Monte Carlo or Saltelli simulations to run. For Saltelli it should be the N in '
                                     'the formula that will make the total number of simulations be equal to N*(D+2)', 
                                required=False, 
                                type=int)
args = aparser.parse_args()

if args.mode == 'montecarlo' and args.num_simulations is None:
    aparser.error('When using the script for montecarlo simulations, the -n argument is required')

out_dir = os.path.realpath(os.path.expandvars(os.path.expanduser(args.output_dir)))
proj_dir = os.path.dirname(os.path.realpath(os.path.expandvars(os.path.expanduser(__file__))))
print(proj_dir)

def create_configuration(configuration_values, config_dir):
    if os.name == 'nt':
        os.system(f'xcopy /E {os.path.join(proj_dir,"CROMO","REACTION")} {config_dir}\\ > nul')
    else:
        os.system(f'cp -rf {os.path.join(proj_dir, "CROMO", "REACTION")} {config_dir}')
    
    selector = open(os.path.join(config_dir, 'SELECTOR.IN'), 'w')
    selector.write(template['CROMO']['selector'].format(**configuration))
    selector.close()
    
    domain = open(os.path.join(config_dir, 'DOMAIN.DAT'), 'w')
    domain.write(template['CROMO']['domain'].format(**configuration))
    domain.close()
    


if not os.path.exists(out_dir):
    print('Output directory does not exist, attempting to create...')
    os.mkdir(out_dir)
if os.name == 'nt':
    os.system(f'copy run_hydrus.bat {out_dir}')
    os.system(f'copy return.txt {out_dir}')
else:
    os.system(f'cp run_hydrus.bat {out_dir}')
    os.system(f'cp return.txt {out_dir}')

('storing mode for later use')
modefile = open(os.path.join(out_dir, 'mode.txt'), 'w')
modefile.write(args.mode)
modefile.close()


print('reading ranges...')
ranges = pd.read_csv(args.ranges)

supported_variables = ['Bulk_d', 'DisperL', 'DisperT', 'DifW', 'SnkL1', 'Conc', 'h', 'ths', 'Ks', 'l']

data = {}
defaults = {}
for _, r in ranges.iterrows():
    if args.mode == 'discrete':
        data[r.variable] = list(np.arange(r.start, r.stop, r.step))
    elif args.mode == 'montecarlo':
        data[r.variable] = np.random.uniform(r.start, r.stop, args.num_simulations)
    defaults[r.variable] = r.default

if args.mode == 'saltelli':
    problem = {
        'num_vars': 10,
        'names': ['Bulk_d', 'DisperL', 'DisperT', 'DifW', 'SnkL1', 'Conc', 'h', 'ths', 'Ks', 'l'],
        'bounds': [[ranges[ranges.variable == supported_variables[0]].start.values[0], ranges[ranges.variable == supported_variables[0]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[1]].start.values[0], ranges[ranges.variable == supported_variables[1]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[2]].start.values[0], ranges[ranges.variable == supported_variables[2]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[3]].start.values[0], ranges[ranges.variable == supported_variables[3]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[4]].start.values[0], ranges[ranges.variable == supported_variables[4]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[5]].start.values[0], ranges[ranges.variable == supported_variables[5]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[6]].start.values[0], ranges[ranges.variable == supported_variables[6]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[7]].start.values[0], ranges[ranges.variable == supported_variables[7]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[8]].start.values[0], ranges[ranges.variable == supported_variables[8]].stop.values[0]],
                   [ranges[ranges.variable == supported_variables[9]].start.values[0], ranges[ranges.variable == supported_variables[9]].stop.values[0]],
                   ]
    }
    

template = {
    'CROMO': {
        'selector': open(os.path.join(proj_dir, 'CROMO', 'PRE', 'SELECTOR.IN')).read(),
        'domain': open(os.path.join(proj_dir, 'CROMO', 'PRE', 'DOMAIN.DAT')).read()
    }
}


configuration_details = defaultdict(dict)

if args.mode == 'discrete':
    e = 0
    for var in supported_variables:
        configuration = defaults.copy()
        for val in data[var]:
            configuration[var] = val
            print(f'Writing configuration {e}')
            config_dir = os.path.join(out_dir, f'configuration_{e}')
            create_configuration(configuration, config_dir)
            configuration_details[var][f'configuration_{e}'] = configuration.copy()
            e += 1
elif args.mode == 'saltelli':
    configurations = saltelli.sample(problem, args.num_simulations, calc_second_order=False)
    for e, conf in enumerate(configurations):
        configuration = {v:k for v,k in zip(supported_variables, conf)}
        print(f'Writing configuration {e}')
        config_dir = os.path.join(out_dir, f'configuration_{e}')
        create_configuration(configuration, config_dir)
        configuration_details[f'configuration_{e}'] = configuration.copy()
else:
    for e in range(args.num_simulations):
        configuration = {}
        for var in supported_variables:
            configuration[var] = data[var][e]
        print(f'Writing configuration {e}')
        config_dir = os.path.join(out_dir, f'configuration_{e}')
        create_configuration(configuration, config_dir)
        configuration_details[f'configuration_{e}'] = configuration.copy()
        e += 1

with open(os.path.join(out_dir, 'configurations.json'), 'w') as outfile:
    json.dump(configuration_details, outfile)


