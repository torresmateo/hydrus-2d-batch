import pandas as pd
import numpy as np

import itertools
import argparse
import os

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

supported_variables = ['Bulk_d', 'DisperL', 'DisperT', 'DifW', 'SnkL1', 'Conc']

data = {}

for _, r in ranges.iterrows():
    data[r.variable] = list(np.arange(r.start, r.stop, r.step))

template = {'CROMO': {'selector':'''Pcp_File_Version=4
*** BLOCK A: BASIC INFORMATION *****************************************
Heading
Welcome to HYDRUS
LUnit  TUnit  MUnit  (indicated units are obligatory for all input data)
cm
hours
mmol
Kat (0:horizontal plane, 1:axisymmetric vertical flow, 2:vertical plane)
  2
MaxIt   TolTh   TolH InitH/W  (max. number of iterations and tolerances)
 100    0.001      1     f
lWat lChem lSink Short Inter lScrn AtmIn lTemp lWTDep lEquil lExtGen lInv
 t     t     f     f     f    t     f     f     f      t      t      f
lUnsatCh lCFSTr   lHP2   m_lActRSU lDummy  lDummy  lDummy
 f       f       f       f       f       f       f
 PrintStep  PrintInterval lEnter
         1              0       t
*** BLOCK B: MATERIAL INFORMATION **************************************
NMat    NLay    hTab1   hTabN     NAniz
  1       1    0.0001   10000
    Model   Hysteresis
      0          0
  thr    ths   Alfa     n         Ks      l
 0.046   0.44  0.146   2.69       29.8    0.6 
*** BLOCK C: TIME INFORMATION ******************************************
        dt       dtMin       dtMax     DMul    DMul2  ItMin ItMax  MPL
     0.0024     0.00024        0.12     1.3     0.7     3     7    10
      tInit        tMax
          0          12
TPrint(1),TPrint(2),...,TPrint(MPL)
        0.5           1         1.5           2           3           5 
          7         9.6        10.8          12 
*** BLOCK D: SOLUTE TRANSPORT INFORMATION *****************************************************
 Epsi  lUpW  lArtD lTDep    cTolA    cTolR   MaxItC    PeCr  Nu.ofSolutes Tortuosity Bacter Filtration
  0.5     f     t     f         0         0     1        2        1         t         f         f
   lWatDep    lInitM   lInitEq    lTortM    lFumigant lDummy    lDummy    lDummy    lDummy    lDummy    lDummy
         f         f         f         f         f         f         f         f         f         f         f
     Bulk.d.     DisperL.      DisperT     Frac      ThImob (1..NMat)
{Bulk_d:>11} {DisperL:>11} {DisperT:>11}           1           0 
         DifW       DifG                n-th solute
{DifW:>11}           0 
         Ks          Nu        Beta       Henry       SnkL1       SnkS1       SnkG1       SnkL1'      SnkS1'      SnkG1'      SnkL0       SnkS0       SnkG0        Alfa
          0           0           1           0 {SnkL1:>11}           0           0           0           0           0           0           0           0           0 
       cTop        cBot
          0         1.1           0           0           0           0           0           0           0 
      tPulse
         24
*** END OF INPUT FILE 'SELECTOR.IN' ************************************
''', 'domain': open(os.path.join(proj_dir, 'CROMO', 'PRE', 'DOMAIN.DAT')).read()} }


configuration_details = ""

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
    

    configuration_details += f'configuration {e} : ' + \
                             str({x: y for x, y in zip(supported_variables, configuration)}) + '\n'

configurations = open(os.path.join(out_dir, 'configurations.txt'), 'w')
configurations.write(configuration_details)
configurations.close()


