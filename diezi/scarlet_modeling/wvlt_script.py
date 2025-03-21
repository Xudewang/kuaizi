import fire
import os
import kuaizi as kz
from kuaizi.fitting import fitting_wavelet_obs_tigress

from astropy.io import fits
from astropy.table import Table

kz.utils.set_env(project='HSC', name='LSBG', data_dir='/tiger/scratch/gpfs/jiaxuanl/Data')

lsbg_cat = Table.read('/tiger/scratch/gpfs/jiaxuanl/Data/HSC/LSBG/Cutout/Candy/candy_cutout_cat.fits')

global_logger = kz.utils.set_logger(logger_name='candy_sample', file_name='candy_log', level='ERROR')

def run_scarlet_wvlt(index):
    blend = fitting_wavelet_obs_tigress(
        {'project': 'HSC', 'name': 'LSBG', 'data_dir': '/tiger/scratch/gpfs/jiaxuanl/Data'},
        lsbg_cat[index],
        name='Seq',
        channels='griz',
        starlet_thresh=0.5,
        prefix='candy',
        show_figure=False,
        global_logger=None)
    return


if __name__ == '__main__':
    fire.Fire(run_scarlet_wvlt)
