import pandas as pd
import numpy as np

import itertools
import argparse
import os
import json

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
                                choices=['montecarlo', 'discrete'])
required_arguments.add_argument('--num-simulations', '-n', help='number of Monte Carlo simulations to run', required=False, 
                                type=int)
args = aparser.parse_args()

if args.mode == 'montecarlo' and args.num_simulations is None:
    aparser.error('When using the script for montecarlo simulations, the -n argument is required')

out_dir = os.path.realpath(os.path.expandvars(os.path.expanduser(args.output_dir)))
proj_dir = os.path.dirname(os.path.realpath(os.path.expandvars(os.path.expanduser(__file__))))
print(proj_dir)

def create_configuration(configuration_values, config_dir):
    if os.name == 'nt':
        os.system(f'xcopy /E {os.path.join(proj_dir,"CROMO","PRE")} {config_dir}\\ > nul')
    else:
        os.system(f'cp -rf {os.path.join(proj_dir, "CROMO", "PRE")} {config_dir}')
    
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

supported_variables = ['Bulk_d', 'DisperL', 'DisperT', 'DifW', 'SnkL1', 'Conc', 'h']

data = {}
defaults = {}
for _, r in ranges.iterrows():
    if args.mode == 'discrete':
        data[r.variable] = list(np.arange(r.start, r.stop, r.step))
    else:
        data[r.variable] = np.random.uniform(r.start, r.stop, args.num_simulations)
    defaults[r.variable] = r.default

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


