"""
Adapted from demo_nas.py
@author: kkorovin@cs.cmu.edu

TODO:
* most of TODO-s are in chemist_opt.gp_bandit
* visualization in mols.visualize

"""

from argparse import Namespace
import time
import os
import shutil

# dragonfly imports
from dragonfly.exd.worker_manager import SyntheticWorkerManager
from dragonfly.utils.reporters import get_reporter

# a few local imports here
from chemist_opt.chemist import optimize_chemist as bo_from_func_caller  # TODO-2
from chemist_opt.mol_function_caller import MolFunctionCaller  # TODO-1
from mols.mol_functions import get_objective_by_name

# if molecular visualization is implemented, use it
try:
    # this function should plot a molecule and draw a synthesis plan
    from mols.visualize import visualize_mol  # TODO-3
except ImportError as e:
    visualize_mol = None


DATASET = "" # TODO

# data directory
MOL_DATA_DIR = 'chembl-data'

# Where to store temporary model checkpoints
EXP_DIR = './experiment_dir_%s'%(time.strftime('%Y%m%d%H%M%S'))
LOG_FILE = os.path.join(EXP_DIR, 'log')

N_WORKERS = 1
BUDGET = 100


# Runner ----------------------------------------------------------------------
def main():
    # Make directories
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    if os.path.exists(EXP_DIR):
        shutil.rmtree(EXP_DIR)
    os.mkdir(EXP_DIR)

    # Obtain a reporter
    reporter = get_reporter(open(LOG_FILE, 'w'))

    objective_func = get_objective_by_name("logp")  # just a function
    train_params = Namespace(data_dir=MOL_DATA_DIR, dataset=DATASET)  # TODO: use this?
    func_caller = MolFunctionCaller(objective_func,
                                    config=None,
                                    train_params=train_params,  # maybe not needed
                                    reporter=reporter)

    worker_manager = SyntheticWorkerManager(num_workers=N_WORKERS, time_distro='const')
    opt_val, opt_point, _ = bo_from_func_caller(func_caller, worker_manager, BUDGET,
                                                is_mf=False,  # not multifidelity for now
                                                reporter=reporter)

    # convert to raw format
    raw_opt_point = func_caller.get_raw_domain_point_from_processed(opt_point)
    opt_mol = raw_opt_point[0]

    # Print the optimal value and visualise the best network.
    reporter.writeln('\nOptimum value found: %0.5f'%(opt_val))
    reporter.writeln('Optimum molecule: %s'%(opt_mol))
    reporter.writeln('Synthesis path: %s'%opt_mol.get_synthesis_path())

    if visualize_mol is not None:
        visualize_file = os.path.join(EXP_DIR, 'optimal_molecule')
        reporter.writeln('Optimal molecule visualized in %s.eps.'%(visualize_file))
        visualize_mol(opt_mol, visualize_file)
    else:
        # TODO
        reporter.writeln('\nInstall graphviz (pip install graphviz) to visualize the molecule.')

if __name__ == "__main__":
    main()
