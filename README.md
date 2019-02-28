# hydrus-2d-batch
A simple tool to run HYDRUS 2D in batch mode

# Requirements

Python 3.6
every library in the `requirements.txt` file, these can be installed by running

```bash
pip install -r requirements.txt
```

# how to use this tool

At the moment, this script only supports the variables listed in the script, and it requires the demo project CROMO (included in this repository)

To run the script, run the following command from the directory containing the `create_projects.py` script

```bash
python create_projects.py --od G:\programming\hydrus --r ranges_sample.csv
```

here, we're assuming that `G:\programming\hydrus` is empty, and `ranges_sample.csv` determines which configurations will be created and its located in the same folder than the `create_projects.py` file.

If successfully done, `G:\programming\hydrus` will contain several HYDRUS projects based on the CROMO project, with the configurations detailed in `G:\programming\hydrus\configurations.txt`

## `ranges.csv`

The file must contain `start`, `stop`, and `step` values for every variable. This will be used to generate values for each variable with a range that goes from `start` to `stop` (non-inclusive) increasing the value by `step`. Some examples below:

* `a,1,10,1` generates values `1 2 3 4 5 6 7 8 9` for variable `a`
* `a,1,10,3` generates values `1 4 7` for variable `a`
* `a,0.1,0.5,0.1` generates values `0.1 0.2 0.3 0.4` for variable `a`

# How to run all the configurations in HYDRUS2D 

Unfortunately, HYDRUS2D does not provide a beautiful way to run projects in batch. This can be done by running the `G:\programming\hydrus\run_hydrus.bat` script as follows.

First, open a command prompt where all the projects are located (`G:\programming\hydrus\`) in our example. Then run the following command

```bat
run_hydrus "C:\Program Files\PC-Progress\HYDRUS 2.xx\H2D_Calc.exe" return.txt
```

This assumes that HYDRUS was installed in `C:\Program Files\PC-Progress\HYDRUS 2.xx\H2D_Calc.exe`. If this is not the case, modify the argument accordingly. If `return.txt` cannot be found, just create it with a single word `return` in it, and save it, This prevents HYDRUS from getting stuck after running each project. 


