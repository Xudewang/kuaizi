'''
python script to deploy slurm jobs for constructing training spectra
'''
import os
import sys
import fire


PREFIX = 'RANDOM_FIELD'
num = 2
OUTPUT_SUBDIR = f'RANDOM_FIELD{num}'
CAT_DIR = f'/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Catalog/random_field{num}/random_field{num}_cutout_cat_random_field{num}.fits'


def deploy_modeling_job(low=0, high=1000, ind_list=None, name=f'random{num}', ncpu=32,
                        method='wavelet', starlet_thresh=0.5, monotonic=True, bkg=True, min_grad=-0.001,
                        variance=0.03**2, scales=[0, 1, 2, 3, 4, 5, 6], sigma=0.05, only_measure=False):
    ''' create slurm script and then submit 
    '''
    time = "11:59:00"

    run_scarlet_content = '\n'.join([f"python ../script/sclt_multiprocess.py --njobs {ncpu} \\",
                                     "   --DATADIR '/scratch/gpfs/jiaxuanl/Data/' \\",
                                     "   --OUTPUT_DIR '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/' \\",
                                     f"   --OUTPUT_SUBDIR '{OUTPUT_SUBDIR}/{method}' \\",
                                     f"   --PREFIX '{PREFIX}' \\",
                                     f"   --cat_dir '{CAT_DIR}' \\",
                                     f"   --low {low} --high {high} \\" if ind_list is None else f"   --ind_list {ind_list} \\",
                                     f"   --suffix '' --starlet_thresh {starlet_thresh} --method {method} \\",
                                     f"   --monotonic {monotonic} --bkg {bkg} --variance {variance} --scales '{scales}' --min_grad {min_grad}"])
    measure_content = '\n'.join([f"python ../script/sclt_meas_mp.py \\",
                                 "    --DATADIR '/scratch/gpfs/jiaxuanl/Data/' \\",
                                 "    --OUTPUT_DIR '/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/' \\",
                                 f"    --OUTPUT_SUBDIR '{OUTPUT_SUBDIR}/{method}' \\",
                                 f"    --PREFIX '{PREFIX}' \\",
                                 f"    --cat_dir '{CAT_DIR}' \\",
                                 f"    --filename '_lsbg_meas_{method}.fits' \\",
                                 f"    --low {low} --high {high} --method {method}\\" if ind_list is None else f"    --ind_list {ind_list} \\",
                                 f"    --ncpu={ncpu} --suffix '' --sigma={sigma}"])
    cntnt = '\n'.join([
        "#!/bin/bash",
        f"#SBATCH -J {name}_{low}_{high}" if ind_list is None else f"#SBATCH -J {name}_ind_list",
        "#SBATCH --nodes=1",
        "#SBATCH --ntasks-per-node=%i" % ncpu,
        "#SBATCH --mem-per-cpu=12G",
        "#SBATCH --time=%s" % time,
        "#SBATCH --export=ALL",
        f"#SBATCH -o ./log/{name}_{low}_{high}.o" if ind_list is None else f"#SBATCH -o ./log/{name}_ind_list.o",
        "#SBATCH --mail-type=all",
        "#SBATCH --mail-user=jiaxuanl@princeton.edu",
        "",
        'now=$(date +"%T")',
        'echo "start time ... $now"',
        "",
        "source /home/jiaxuanl/Research/Packages/kuaizi/diezi/setup_env.sh",
        "export OMP_NUM_THREADS=1",
        "",
        run_scarlet_content if not only_measure else "",
        "",
        measure_content,
        "",
        "",
        'now=$(date +"%T")',
        'echo "end time ... $now"',
        ""])

    # create the slurm script execute it and remove it
    if not os.path.isdir('./slurm'):
        os.mkdir('./slurm')
    f = open(f'./slurm/_{name}_{low}_{high}.slurm', 'w') if ind_list is None else open(
        f'./slurm/_{name}_ind_list.slurm', 'w')
    f.write(cntnt)
    f.close()
    os.system(f'sbatch ./slurm/_{name}_{low}_{high}.slurm') if ind_list is None else os.system(
        f'sbatch ./slurm/_{name}_ind_list.slurm')

    #os.system('rm _train.slurm')
    return None


if __name__ == '__main__':
    fire.Fire(deploy_modeling_job)


############ VANILLA #############
# python deploy_random2.py --name random1 --ncpu=12 --method=vanilla \
# --low=0 --high=None --monotonic=True --bkg=True -min_grad=-0.02 --sigma=0.05 --only_measure=True

############ SPERGEL #############
# python deploy_random2.py --name rdm1_spgl --ncpu=12 --method=spergel \
# --low=0 --high=None --monotonic=True --bkg=True -min_grad=-0.1 --sigma=0.05

# python deploy_random2.py --name rdm2_spgl --ncpu=12 --method=spergel --low=0 --high=None --monotonic=True --bkg=True --min_grad=-0.05
