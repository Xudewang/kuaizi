#!/bin/bash
#SBATCH --job-name=sclt_v_1k       # create a short name for your job
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --cpus-per-task=1       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=32G         # memory per cpu-core (4G per cpu-core is default)
#SBATCH --time=48:00:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=all          # send email when job begins, ends and fails
#SBATCH --mail-user=jiaxuanl@princeton.edu

module purge
. /home/jiaxuanl/Research/Packages/kuaizi/diezi/setup_env.sh
export OMP_NUM_THREADS=1

# python3 wvlt_multiprocess.py --njobs 4 --ind_list "[51, 53, 110, 112, 196]" --suffix "_complement" --starlet_thresh 0.5

# python3 vanilla_multiprocess.py --njobs 5 --cat_dir '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Cutout/NSA/nsa_cutout_cat_1103.fits' --ind_list "[ 11,  57, 123, 137, 152, 160, 170, 183, 234, 237, 260, 268, 289, 293, 297, 314, 336, 387]" --suffix "" --starlet_thresh 0.5

#python3 vanilla_multiprocess.py --njobs 1 --cat_dir '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Catalog/NSA/z002_004/nsa_cutout_cat_z002_004.fits' --ind_list "[1122, 1144, 1165]" --suffix "" --starlet_thresh 0.5
python3 vanilla_multiprocess.py --njobs 40 --cat_dir '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Catalog/NSA/z002_004/nsa_cutout_cat_z002_004.fits' --low 0 --high 1000 --suffix "" --starlet_thresh 0.5
# python3 vanilla_multiprocess.py --njobs 10 --cat_dir '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Cutout/NSA/nsa_cutout_cat_1103.fits' --low 0 --high 501 --suffix "" --starlet_thresh 0.5