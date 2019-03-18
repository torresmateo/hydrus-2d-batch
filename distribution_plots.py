import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


aparser = argparse.ArgumentParser()
required_arguments = aparser.add_argument_group('required arguments')
required_arguments.add_argument('--pickle-dir', '-pd',
                                help='path to a directory where many of the results.pkl files are contained', 
                                required=True)
required_arguments.add_argument('--estimator-step', '-m',
                                help='number of simulations to consider for the plot', required=True, type=int)
required_arguments.add_argument('--bins', '-b',
                                help='number of bins to consider for the distribution plot', required=True, 
                                default=20, type=int)
required_arguments.add_argument('--mean', help='if incuded, the plot shows the mean', action='store_true')
required_arguments.add_argument('--std', help='if incuded, the plot shows the standard deviation', action='store_true')
required_arguments.add_argument('--bars', help='if incuded, the plot shows the histogram bars', action='store_true')

args = aparser.parse_args()

res_dir = os.path.realpath(args.pickle_dir)

results = None
for e, res in enumerate(os.listdir(res_dir)):
    if res.endswith('.pkl'):
        print(f'reading file: {res}')
        if results is None:
            results = pd.read_pickle(os.path.join(res_dir,res))
            idx = results.groupby(['configuration'])['t'].transform(max) == results['t']
            results = results[idx]
            results.configuration = results.configuration.astype(str) + f' {e}'
        else:
            df = pd.read_pickle(os.path.join(res_dir,res))
            idx = df.groupby(['configuration'])['t'].transform(max) == df['t']
            df = df[idx]
            df.configuration = df.configuration.astype(str) + f' x{e}'
            results = results.append(df)
print('generating images...')

cumchs = results.CumCh1.values
n = args.estimator_step
fig, ax = plt.subplots(figsize=(10,10))
for i in range(cumchs.shape[0]//n):
    sns.distplot(cumchs[:n*i+n], ax=ax, hist=args.bars, label=f'{i*n+n}', bins=args.bins)
    if args.mean:
        ax.axvline(cumchs[:n*i+n].mean(), label=f'$\mu$ {i*n+n}', linestyle='--', color='r')
    if args.std:
        ax.axvline(cumchs[:n*i+n].mean() + cumchs[:n*i+n].std(), label=f'$1\sigma$ {i*n+n}', linestyle='--', color='g')
        ax.axvline(cumchs[:n*i+n].mean() - cumchs[:n*i+n].std(), label=f'$-1\sigma$ {i*n+n}', linestyle='--', color='g')
fig.legend()
ax.set_ylabel('normalised frequency')
ax.set_xlabel('CumCh1')
plt.savefig(os.path.join(res_dir, f'distributions {n}.png'))
plt.savefig(os.path.join(res_dir, f'distributions {n}.svg'))
plt.close('all')

last_bins = np.zeros(args.bins)
diff = []
simulations=[]
for i in range(cumchs.shape[0]//n):
    hist, bin_edges = np.histogram(cumchs[:n*i+n], density=True, bins=args.bins)
    #print(i, np.sum(np.abs(hist**2 - last_bins**2)))
    diff.append(np.mean(np.square(hist - last_bins)))
    simulations.append(cumchs[:n*i+n].shape)
    last_bins = hist
fig, ax = plt.subplots(figsize=(10,10))
ax.set_yscale('log')
ax.plot(simulations, diff)
ax.set_ylabel('mean squared error to previous distribution')
ax.set_xlabel('number of simulations considered')
plt.savefig(os.path.join(res_dir, f'convergence_{n}.png'))
plt.savefig(os.path.join(res_dir, f'convergence_{n}.svg'))

plt.close('all')

last_bins = np.zeros(args.bins)
diff = []
simulations=[]
for i in range(cumchs.shape[0]//n):
    hist, bin_edges = np.histogram(cumchs[:n*i+n], density=True, bins=args.bins)
    #print(i, np.sum(np.abs(hist**2 - last_bins**2)))
    diff.append(np.mean(np.square(hist - last_bins)))
    simulations.append(cumchs[:n*i+n].shape)
    last_bins = hist
fig, ax = plt.subplots(figsize=(10,10))
ax.plot(simulations, diff)
ax.set_ylabel('mean squared error to previous distribution')
ax.set_xlabel('number of simulations considered')
plt.savefig(os.path.join(res_dir, f'convergence_regular_{n}.png'))
plt.savefig(os.path.join(res_dir, f'convergence_regular_{n}.svg'))