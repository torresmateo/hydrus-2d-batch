import argparse
import pandas as pd
import os

aparser = argparse.ArgumentParser()
required_arguments = aparser.add_argument_group('required arguments')
required_arguments.add_argument('--pickle-dir', '-pd',
                                help='path to a directory where many of the results.pkl files are contained', 
                                required=True)
args = aparser.parse_args()

res_dir = os.path.realpath(args.pickle_dir)

for e, res in enumerate(os.listdir(res_dir)):
    if res.endswith('.pkl'):
        print(f'reading file: {res}')
        results = pd.read_pickle(os.path.join(res_dir,res))
        if 'group' in results.columns:
            print(f'creating excel file for variable {group}')
            for group in results.group.unique():
                idx = results['group'] == group
                results[idx].to_excel(os.path.join(res_dir, f'results {e} {group}.xlsx'))
