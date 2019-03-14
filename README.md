# hydrus-2d-batch
A simple tool to run HYDRUS 2D in batch mode

# Requirements

Python 3.6 or newer

Every library in the `requirements.txt` file, these can be installed by running the following command on a terminal 

```bash
pip install -r requirements.txt
```

If `pip` is not installed in your computer, please try `pip3` instead.

# how to use this tool

There are two parts to this tool. To create projects, and to analyse the results.

## create projects
At the moment, this script only supports the variables listed in the script, and it requires the demo project CROMO (included in this repository)

To run the script, run the following command from the directory containing the `create_projects.py` script

```bash
python create_projects.py -od G:\programming\hydrus -r ranges_sample.csv -m discrete
```

here, we're assuming that `G:\programming\hydrus` is empty, and `ranges_sample.csv` determines which configurations will be created and its located in the same folder than the `create_projects.py` file. The `-m` argument refers to whether the simulations will follow a Monte Carlo sampling procedure or not. The example above describes a 'discrete' approach, for a Monte Carlo sampling run:

```bash
python create_projects.py -od G:\programming\hydrus -r ranges_sample.csv -m montecarlo -n 1000
```

This adds the `-n` argument, which indicates the number of configurations to be sampled. 

If successfully done, `G:\programming\hydrus` will contain several HYDRUS projects based on the CROMO project, with the configurations detailed in `G:\programming\hydrus\configurations.json`

### `ranges.csv`

The file must contain `start`, `stop`, `step`, and `default` values for every variable. This will be used to generate values for each variable with a range that goes from `start` to `stop` (non-inclusive) increasing the value by `step`. Some examples below:

* `a,1,10,1` generates values `1 2 3 4 5 6 7 8 9` for variable `a`
* `a,1,10,3` generates values `1 4 7` for variable `a`
* `a,0.1,0.5,0.1` generates values `0.1 0.2 0.3 0.4` for variable `a`

The `default` value will be used when the variable is not being analysed. This will generate files that allow the results to be grouped by analysed variable afterwards.

If `montecarlo` is used as the mode, only values set in `start` and `stop` will be considered, and values in the open interval `[start, stop)`. Results will not be grouped by variable by the results aggregation script. For more details on the sampling, please read [numpy's uniform distribution documentation](https://docs.scipy.org/doc/numpy/reference/generated/numpy.random.uniform.html#numpy.random.uniform).

### How to run all the configurations in HYDRUS2D 

Unfortunately, HYDRUS2D does not provide a beautiful way to run projects in batch. This can be done by running the `G:\programming\hydrus\run_hydrus.bat` script as follows.

First, open a command prompt where all the projects are located (`G:\programming\hydrus\`) in our example. Then run the following command

```bat
run_hydrus "C:\Program Files\PC-Progress\HYDRUS 2.xx\H2D_Calc.exe" return.txt
```

This assumes that HYDRUS was installed in `C:\Program Files\PC-Progress\HYDRUS 2.xx\H2D_Calc.exe`. If this is not the case, modify the argument accordingly. If `return.txt` cannot be found, just create it with a single word `return` in it, and save it, This prevents HYDRUS from getting stuck after running each project. 

## analyse the results

Once HYDRUS has finished running, all the folders will have files with the `out` extension.

This script will extract the `CumCh1` variable from the `solute1.out` output file, aggregate it over all the configurations, and save it for further analysis. 
You simply need to run the following command

```bash
python aggregate_results.py -rd G:\programming\hydrus
```

2 files will be created: 
* `results.pkl` containing a pandas DataFrame for easy analysis with python
* `results.xlsx` The same data in Microsoft Excel format.
* `res.mat` The same data in MATLAB format. Please refer to the `plots.m` script for examples on how to use this data.