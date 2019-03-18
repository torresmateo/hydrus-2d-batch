import argparse
import os
import sys
import json
import pandas as pd
import scipy.io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from SoluteParser import SoluteParser


aparser = argparse.ArgumentParser()
required_arguments = aparser.add_argument_group('required arguments')
required_arguments.add_argument('--results-dir', '-rd',
                                help='path to the directory containing all the configurations. Results will be stored '
                                     'in that directory', required=True)
required_arguments.add_argument('--estimator-step', '-m',
                                help='number of simulations to consider for the plot', required=True, type=int)
args = aparser.parse_args()

res_dir = os.path.realpath(args.results_dir)

supported_variables = ['Bulk_d', 'DisperL', 'DisperT', 'DifW', 'SnkL1', 'Conc', 'h', 'ths', 'Ks', 'l']

with open(os.path.join(res_dir, 'mode.txt')) as modefile:
    mode = modefile.read().strip()

with open(os.path.join(res_dir, 'configurations.json')) as configurations:
    configuration_details = json.load(configurations)


if mode == 'discrete':
    data = {var: [] for var in supported_variables + ['t', 'CumCh1', 'configuration', 'group']}
    for var in supported_variables:
        for conf_dir in configuration_details[var].keys():
            print(f'extracting results from {conf_dir}')
            if not os.path.isdir(os.path.join(res_dir, conf_dir)):
                continue
            solute_file = os.path.join(res_dir, conf_dir, 'solute1.out')
            if not os.path.exists(solute_file):
                print(f'{conf_dir} does not contain the expected result file, please run HYDRUS before running this script')
                sys.exit(1)
            solute = SoluteParser(solute_file)
            for t, cum_ch in solute:
                for v in supported_variables:
                    data[v].append(configuration_details[var][conf_dir][v])
                data['configuration'].append(conf_dir.replace('_', ' ').replace('configuration', 'config'))
                data['t'].append(float(t))
                data['CumCh1'].append(float(cum_ch))
                data['group'].append(var)
elif mode == 'montecarlo':
    data = {var: [] for var in supported_variables + ['t', 'CumCh1', 'configuration']}
    for conf_dir in configuration_details.keys():
        print(f'extracting results from {conf_dir}')
        if not os.path.isdir(os.path.join(res_dir, conf_dir)):
            continue
        solute_file = os.path.join(res_dir, conf_dir, 'solute1.out')
        if not os.path.exists(solute_file):
            print(f'{conf_dir} does not contain the expected result file, please run HYDRUS before running this script')
            sys.exit(1)
        solute = SoluteParser(solute_file)
        for t, cum_ch in solute:
            for v in supported_variables:
                data[v].append(configuration_details[conf_dir][v])
            data['configuration'].append(conf_dir.replace('_', ' ').replace('configuration', 'config'))
            data['t'].append(float(t))
            data['CumCh1'].append(float(cum_ch))
    
print(f'formatting results...')
df = pd.DataFrame(data)
print(f'saving pickle file...')
df.to_pickle(os.path.join(res_dir, 'results.pkl'))
print(f'saving excel file...')
df.to_excel(os.path.join(res_dir, 'results.xlsx'))
print(f'saving MATLAB file...')
scipy.io.savemat(os.path.join(res_dir, 'res.mat'), mdict={'res':df.values[:,:9], 'other':df.values[:,9:]})

print('creating distribution estimation figure')
idx = df.groupby(['configuration'])['t'].transform(max) == df['t']
cumchs = df[idx].CumCh1.values
n = args.estimator_step
fig, ax = plt.subplots(figsize=(10,10))
for i in range(cumchs.shape[0]//n):
    print(cumchs[:n*i+n].shape)
    sns.distplot(cumchs[:n*i+n], ax=ax, hist=True, label=f'{i*n+n}')
fig.legend()
plt.savefig(os.path.join(res_dir, 'distributions.png'))
plt.savefig(os.path.join(res_dir, 'distributions.svg'))

