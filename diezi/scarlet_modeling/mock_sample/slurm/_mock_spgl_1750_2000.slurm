#!/bin/bash
#SBATCH -J mock_spgl_1750_2000
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem-per-cpu=10G
#SBATCH --time=11:59:00
#SBATCH --export=ALL
#SBATCH -o ./log/mock_spgl_1750_2000.o
#SBATCH --mail-type=all
#SBATCH --mail-user=jiaxuanl@princeton.edu

now=$(date +"%T")
echo "start time ... $now"

source /home/jiaxuanl/Research/Packages/kuaizi/diezi/setup_env.sh
export OMP_NUM_THREADS=1

python ../script/sclt_multiprocess.py --njobs 16 \
   --DATADIR '/scratch/gpfs/jiaxuanl/Data/' \
   --OUTPUT_DIR '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/' \
   --OUTPUT_SUBDIR 'MOCK_SAMPLE/spergel' \
   --PREFIX 'MOCK' \
   --cat_dir '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Catalog/mock_sample/mock_obj_cat_0_2000.fits' \
   --low 1750 --high 2000 \
   --suffix '' --starlet_thresh 0.5 --method spergel \
   --monotonic True --bkg True --variance 0.0009 --scales '[0, 1, 2, 3, 4, 5, 6]' --min_grad 0.002

python ../script/sclt_meas_mp.py \
    --DATADIR '/scratch/gpfs/jiaxuanl/Data/' \
    --OUTPUT_DIR '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/' \
    --OUTPUT_SUBDIR 'MOCK_SAMPLE/spergel' \
    --PREFIX 'MOCK' \
    --cat_dir '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Catalog/mock_sample/mock_obj_cat_0_2000.fits' \
    --filename '_lsbg_meas_spergel_monotonic.fits' \
    --low 1750 --high 2000 --method spergel\
    --ncpu=16 --suffix '' --sigma=None


now=$(date +"%T")
echo "end time ... $now"
