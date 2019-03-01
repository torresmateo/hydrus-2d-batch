import pandas as pd
import numpy as np

import itertools
import argparse
import os
import json

aparser = argparse.ArgumentParser()
required_arguments = aparser.add_argument_group('required arguments')
required_arguments.add_argument('--output-dir', '--od',
                                help='a path to a suitable folder (ideally empty) where the new configurations will '
                                     'be stored', required=True)
required_arguments.add_argument('--ranges', '--r',
                                help='a csv file that determines the values to infer', required=True)
args = aparser.parse_args()

out_dir = os.path.realpath(os.path.expandvars(os.path.expanduser(args.output_dir)))
proj_dir = os.path.dirname(os.path.realpath(os.path.expandvars(os.path.expanduser(__file__))))
print(proj_dir)

if not os.path.exists(out_dir):
    print('Output directory does not exist, attempting to create...')
    os.mkdir(out_dir)
if os.name == 'nt':
    os.system(f'copy run_hydrus.bat {out_dir}')
    os.system(f'copy return.txt {out_dir}')
else:
    os.system(f'cp run_hydrus.bat {out_dir}')
    os.system(f'cp return.txt {out_dir}')

print('reading ranges...')
ranges = pd.read_csv(args.ranges)

supported_variables = ['Bulk_d', 'DisperL', 'DisperT', 'DifW', 'SnkL1', 'Conc', 'h']

data = {}

for _, r in ranges.iterrows():
    data[r.variable] = list(np.arange(r.start, r.stop, r.step))

template = {
    'CROMO': {
        'selector': open(os.path.join(proj_dir, 'CROMO', 'PRE', 'SELECTOR.IN')).read(),
        'domain': open(os.path.join(proj_dir, 'CROMO', 'PRE', 'DOMAIN.DAT')).read()
    }
}


configuration_details = {}

for e, configuration in enumerate(itertools.product(*[data[k] for k in supported_variables])):
    print(f'Writing configuration {e}')
    config_dir = os.path.join(out_dir, f'configuration_{e}\\')
    if os.name == 'nt':
        os.system(f'xcopy /E {os.path.join(proj_dir,"CROMO","PRE")} {config_dir}')
    else:
        os.system(f'cp -rf {os.path.join(proj_dir, "CROMO", "PRE")} {config_dir}')
    
    selector = open(os.path.join(config_dir, 'SELECTOR.IN'), 'w')
    selector.write(template['CROMO']['selector'].format(**{x: y for x, y in zip(supported_variables, configuration)}))
    selector.close()
    
    domain = open(os.path.join(config_dir, 'DOMAIN.DAT'), 'w')
    domain.write(template['CROMO']['domain'].format(**{x: y for x, y in zip(supported_variables, configuration)}))
    domain.close()
    
    configuration_details[f'configuration_{e}'] = {x: y for x, y in zip(supported_variables, configuration)}

    if e >= 10:
        break

with open(os.path.join(out_dir, 'configurations.json'), 'w') as outfile:
    json.dump(configuration_details, outfile)


