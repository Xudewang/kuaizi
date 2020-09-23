from __future__ import division, print_function
import os

import numpy as np

from astropy.io import fits
from astropy import wcs
from astropy.table import Table
from astropy.visualization import (ZScaleInterval,
                                   AsymmetricPercentileInterval)
from astropy.visualization import make_lupton_rgb
from astropy.stats import sigma_clip, SigmaClip, sigma_clipped_stats

from matplotlib import colors
from matplotlib import rcParams
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import NullFormatter, MaxNLocator, FormatStrFormatter, AutoMinorLocator
from matplotlib.patches import Ellipse, Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from palettable.colorbrewer.sequential import (Greys_9,
                                               OrRd_9,
                                               Blues_9,
                                               Purples_9,
                                               YlGn_9)


def random_cmap(ncolors=256, background_color='white'):
    """Random color maps, from ``kungpao`` https://github.com/dr-guangtou/kungpao. 

    Generate a matplotlib colormap consisting of random (muted) colors.
    A random colormap is very useful for plotting segmentation images.

    Parameters
        ncolors : int, optional
            The number of colors in the colormap.  The default is 256.
        random_state : int or ``~numpy.random.RandomState``, optional
            The pseudo-random number generator state used for random
            sampling.  Separate function calls with the same
            ``random_state`` will generate the same colormap.

    Returns
        cmap : `matplotlib.colors.Colormap`
            The matplotlib colormap with random colors.

    Notes
        Based on: colormaps.py in photutils

    """
    prng = np.random.mtrand._rand

    h = prng.uniform(low=0.0, high=1.0, size=ncolors)
    s = prng.uniform(low=0.2, high=0.7, size=ncolors)
    v = prng.uniform(low=0.5, high=1.0, size=ncolors)

    hsv = np.dstack((h, s, v))
    rgb = np.squeeze(colors.hsv_to_rgb(hsv))

    if background_color is not None:
        if background_color not in colors.cnames:
            raise ValueError('"{0}" is not a valid background color '
                             'name'.format(background_color))
        rgb[0] = colors.hex2color(colors.cnames[background_color])

    return colors.ListedColormap(rgb)

# About the Colormaps
IMG_CMAP = plt.get_cmap('viridis')
IMG_CMAP.set_bad(color='black')
SEG_CMAP = random_cmap(ncolors=512, background_color=u'white')
SEG_CMAP.set_bad(color='white')
SEG_CMAP.set_under(color='white')

BLK = Greys_9.mpl_colormap
ORG = OrRd_9.mpl_colormap
BLU = Blues_9.mpl_colormap
GRN = YlGn_9.mpl_colormap
PUR = Purples_9.mpl_colormap

def display_single(img,
                   pixel_scale=0.168,
                   physical_scale=None,
                   xsize=8,
                   ysize=8,
                   ax=None,
                   stretch='arcsinh',
                   scale='zscale',
                   contrast=0.25,
                   no_negative=False,
                   lower_percentile=1.0,
                   upper_percentile=99.0,
                   cmap=IMG_CMAP,
                   scale_bar=True,
                   scale_bar_length=5.0,
                   scale_bar_fontsize=20,
                   scale_bar_y_offset=0.5,
                   scale_bar_color='w',
                   scale_bar_loc='left',
                   color_bar=False,
                   color_bar_loc=1,
                   color_bar_width='75%',
                   color_bar_height='5%',
                   color_bar_fontsize=18,
                   color_bar_color='w',
                   add_text=None,
                   text_fontsize=30,
                   text_y_offset=0.80,
                   text_color='w'):
    """
    Display single image using ``arcsinh`` stretching, "zscale" scaling and ``viridis`` colormap as default. 
    This function is from ``kungpao`` https://github.com/dr-guangtou/kungpao.

    Parameters:
        img (numpy 2-D array): The image array.
        pixel_scale (float): The pixel size, in unit of "arcsec/pixel".
        physical_scale (bool): Whether show the image in physical scale.
        xsize (int): Width of the image, default = 8. 
        ysize (int): Height of the image, default = 8. 
        ax (``matplotlib.pyplot.axes`` object): The user could provide axes on which the figure will be drawn.
        stretch (str): Stretching schemes. Options are "arcsinh", "log", "log10" and "linear".
        scale (str): Scaling schemes. Options are "zscale" and "percentile".
        contrast (float): Contrast of figure.
        no_negative (bool): If true, all negative pixels will be set to zero.
        lower_percentile (float): Lower percentile, if using ``scale="percentile"``.
        upper_percentile (float): Upper percentile, if using ``scale="percentile"``.
        cmap (str): Colormap.
        scale_bar (bool): Whether show scale bar or not.
        scale_bar_length (float): The length of scale bar.
        scale_bar_y_offset (float): Offset of scale bar on y-axis.
        scale_bar_fontsize (float): Fontsize of scale bar ticks.
        scale_bar_color (str): Color of scale bar.
        scale_bar_loc (str): Scale bar position, options are "left" and "right".
        color_bar (bool): Whether show colorbar or not.
        add_text (str): The text you want to add to the figure. Note that it is wrapped within ``$\mathrm{}$``.
        text_fontsize (float): Fontsize of text.
        text_y_offset (float): Offset of text on y-axis.
        text_color (str): Color of text.

    Returns:
        ax: If the input ``ax`` is not ``None``.

    """

    if ax is None:
        fig = plt.figure(figsize=(xsize, ysize))
        ax1 = fig.add_subplot(111)
    else:
        ax1 = ax

    # Stretch option
    if stretch.strip() == 'arcsinh':
        img_scale = np.arcsinh(img)
    elif stretch.strip() == 'log':
        if no_negative:
            img[img <= 0.0] = 1.0E-10
        img_scale = np.log(img)
    elif stretch.strip() == 'log10':
        if no_negative:
            img[img <= 0.0] = 1.0E-10
        img_scale = np.log10(img)
    elif stretch.strip() == 'linear':
        img_scale = img
    else:
        raise Exception("# Wrong stretch option.")

    # Scale option
    if scale.strip() == 'zscale':
        try:
            zmin, zmax = ZScaleInterval(contrast=contrast).get_limits(img_scale)
        except IndexError:
            # TODO: Deal with problematic image
            zmin, zmax = -1.0, 1.0
    elif scale.strip() == 'percentile':
        try:
            zmin, zmax = AsymmetricPercentileInterval(
                lower_percentile=lower_percentile,
                upper_percentile=upper_percentile).get_limits(img_scale)
        except IndexError:
            # TODO: Deal with problematic image
            zmin, zmax = -1.0, 1.0
    else:
        zmin, zmax = np.nanmin(img_scale), np.nanmax(img_scale)
    
    show = ax1.imshow(img_scale, origin='lower', cmap=cmap,
                      vmin=zmin, vmax=zmax)

    # Hide ticks and tick labels
    ax1.tick_params(
        labelbottom=False,
        labelleft=False,
        axis=u'both',
        which=u'both',
        length=0)
    #ax1.axis('off')

    # Put scale bar on the image
    (img_size_x, img_size_y) = img.shape
    if physical_scale is not None:
        pixel_scale *= physical_scale
    if scale_bar:
        if scale_bar_loc == 'left':
            scale_bar_x_0 = int(img_size_x * 0.04)
            scale_bar_x_1 = int(img_size_x * 0.04 +
                                (scale_bar_length / pixel_scale))
        else:
            scale_bar_x_0 = int(img_size_x * 0.95 -
                                (scale_bar_length / pixel_scale))
            scale_bar_x_1 = int(img_size_x * 0.95)
        scale_bar_y = int(img_size_y * 0.10)
        scale_bar_text_x = (scale_bar_x_0 + scale_bar_x_1) / 2
        scale_bar_text_y = (scale_bar_y * scale_bar_y_offset)
        if physical_scale is not None:
            if scale_bar_length > 1000:
                scale_bar_text = r'$%d\ \mathrm{Mpc}$' % int(scale_bar_length / 1000)
            else:
                scale_bar_text = r'$%d\ \mathrm{kpc}$' % int(scale_bar_length)
        else:
            if scale_bar_length < 60:
                scale_bar_text = r'$%d^{\prime\prime}$' % int(scale_bar_length)
            elif 60 < scale_bar_length < 3600:
                scale_bar_text = r'$%d^{\prime}$' % int(scale_bar_length / 60)
            else: 
                scale_bar_text = r'$%d^{\circ}$' % int(scale_bar_length / 3600)
        scale_bar_text_size = scale_bar_fontsize

        ax1.plot(
            [scale_bar_x_0, scale_bar_x_1], [scale_bar_y, scale_bar_y],
            linewidth=3,
            c=scale_bar_color,
            alpha=1.0)
        ax1.text(
            scale_bar_text_x,
            scale_bar_text_y,
            scale_bar_text,
            fontsize=scale_bar_text_size,
            horizontalalignment='center',
            color=scale_bar_color)
    if add_text is not None:
        text_x_0 = int(img_size_x*0.08)
        text_y_0 = int(img_size_y*text_y_offset)
        ax1.text(text_x_0, text_y_0, r'$\mathrm{'+add_text+'}$', fontsize=text_fontsize, color=text_color)

    # Put a color bar on the image
    if color_bar:
        ax_cbar = inset_axes(ax1,
                             width=color_bar_width,
                             height=color_bar_height,
                             loc=color_bar_loc)
        if ax is None:
            cbar = plt.colorbar(show, ax=ax1, cax=ax_cbar,
                                orientation='horizontal')
        else:
            cbar = plt.colorbar(show, ax=ax, cax=ax_cbar,
                                orientation='horizontal')

        cbar.ax.xaxis.set_tick_params(color=color_bar_color)
        cbar.ax.yaxis.set_tick_params(color=color_bar_color)
        cbar.outline.set_edgecolor(color_bar_color)
        plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'),
                 color=color_bar_color, fontsize=color_bar_fontsize)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'),
                 color=color_bar_color, fontsize=color_bar_fontsize)

    if ax is None:
        return fig
    return ax1

def display_multiple(data_array, text=None, ax=None, scale_bar=True, **kwargs):
    """
    Display multiple images together using the same strecth and scale.

    Parameters:
        data_array (list): A list containing images which are numpy 2-D arrays.
        text (str): A list containing strings which you want to add to each panel.
        ax (list): The user could provide a list of axes on which the figure will be drawn.
        **kwargs: other arguments in ``display_single``.

    Returns:
        axes: If the input ``ax`` is not ``None``.

    """
    if ax is None:
        fig, axes = plt.subplots(1, len(data_array), figsize=(len(data_array) * 4, 8))
    else:
        axes = ax

    if text is None:
        _, zmin, zmax = _display_single(data_array[0], ax=axes[0], scale_bar=scale_bar, **kwargs)
    else:
        _, zmin, zmax = _display_single(data_array[0], add_text=text[0], ax=axes[0], scale_bar=scale_bar, **kwargs)
    for i in range(1, len(data_array)):
        if text is None:
            _display_single(data_array[i], ax=axes[i], scale_manual=[zmin, zmax], scale_bar=False, **kwargs)
        else:
            _display_single(data_array[i], add_text=text[i], ax=axes[i], scale_manual=[zmin, zmax], scale_bar=False, **kwargs)

    plt.subplots_adjust(wspace=0.0)
    if ax is None:
        return fig
    else:
        return axes

def draw_circles(img, catalog, colnames=['x', 'y'], header=None, ax=None, circle_size=30, 
                 pixel_scale=0.168, color='r', **kwargs):
    """
    Draw circles on an image according to a catalogue. 

    Parameters:
        img (numpy 2-D array): Image itself.
        catalog (``astropy.table.Table`` object): A catalog which contains positions.
        colnames (list): List of string, indicating which columns correspond to positions. 
            It can also be "ra" and "dec", but then "header" is needed.
        header: Header file of a FITS image containing WCS information, typically ``astropy.io.fits.header`` object.  
        ax (``matplotlib.pyplot.axes`` object): The user could provide axes on which the figure will be drawn.
        circle_size (float): Radius of circle, in pixel.
        pixel_scale (float): Pixel size, in arcsec/pixel. Needed for correct scale bar.
        color (str): Color of circles.
        **kwargs: other arguments of ``display_single``. 

    Returns:
        ax: If the input ``ax`` is not ``None``.

    """
    if ax is None:
        fig = plt.figure(figsize=(12, 12))
        fig.subplots_adjust(left=0.0, right=1.0, 
                            bottom=0.0, top=1.0,
                            wspace=0.00, hspace=0.00)
        gs = gridspec.GridSpec(2, 2)
        gs.update(wspace=0.0, hspace=0.00)
        ax1 = fig.add_subplot(gs[0])
    else:
        ax1 = ax

    #ax1.yaxis.set_major_formatter(NullFormatter())
    #ax1.xaxis.set_major_formatter(NullFormatter())
    ax1.axis('off')
    
    from matplotlib.patches import Ellipse, Rectangle
    if np.any([item.lower() == 'ra' for item in colnames]): 
        if header is None:
            raise ValueError('# Header containing WCS must be provided to convert sky coordinates into image coordinates.')
            return
        else:
            w = wcs.WCS(header)
            x, y = w.wcs_world2pix(Table(catalog)[colnames[0]].data.data, 
                                   Table(catalog)[colnames[1]].data.data, 0)
    else:
        x, y = catalog[colnames[0]], catalog[colnames[1]]
    display_single(img, ax=ax1, pixel_scale=pixel_scale, **kwargs)
    for i in range(len(catalog)):
        e = Ellipse(xy=(x[i], y[i]),
                        height=circle_size,
                        width=circle_size,
                        angle=0)
        e.set_facecolor('none')
        e.set_edgecolor(color)
        e.set_alpha(0.7)
        e.set_linewidth(1.3)
        ax1.add_artist(e)
    if ax is not None:
        return ax

def draw_rectangles(img, catalog, colnames=['x', 'y'], header=None, ax=None, rectangle_size=[30, 30], 
                    pixel_scale=0.168, color='r', **kwargs):
    """
    Draw rectangles on an image according to a catalogue. 

    Parameters:
        img (numpy 2-D array): Image itself.
        catalog (``astropy.table.Table`` object): A catalog which contains positions.
        colnames (list): List of string, indicating which columns correspond to positions. 
            It can also be "ra" and "dec", but then "header" is needed.
        header: Header file of a FITS image containing WCS information, typically ``astropy.io.fits.header`` object.  
        ax (``matplotlib.pyplot.axes`` object): The user could provide axes on which the figure will be drawn.
        rectangle_size (list of floats): Size of rectangles, in pixel.
        pixel_scale (float): Pixel size, in arcsec/pixel. Needed for correct scale bar.
        color (str): Color of rectangles.
        **kwargs: other arguments of ``display_single``. 

    Returns:
        ax: If the input ``ax`` is not ``None``.
        
    """
    if ax is None:
        fig = plt.figure(figsize=(12, 12))
        fig.subplots_adjust(left=0.0, right=1.0, 
                            bottom=0.0, top=1.0,
                            wspace=0.00, hspace=0.00)
        gs = gridspec.GridSpec(2, 2)
        gs.update(wspace=0.0, hspace=0.00)
        ax1 = fig.add_subplot(gs[0])
    else:
        ax1 = ax

    #ax1.yaxis.set_major_formatter(NullFormatter())
    #ax1.xaxis.set_major_formatter(NullFormatter())
    #ax1.axis('off')
    
    from matplotlib.patches import Rectangle
    if np.any([item.lower() == 'ra' for item in colnames]): 
        if header is None:
            raise ValueError('# Header containing WCS must be provided to convert sky coordinates into image coordinates.')
            return
        else:
            w = wcs.WCS(header)
            x, y = w.wcs_world2pix(Table(catalog)[colnames[0]].data.data, 
                                   Table(catalog)[colnames[1]].data.data, 0)
    else:
        x, y = catalog[colnames[0]], catalog[colnames[1]]
    display_single(img, ax=ax1, pixel_scale=pixel_scale, **kwargs)
    for i in range(len(catalog)):
        e = Rectangle(xy=(x[i] - rectangle_size[0] // 2, 
                          y[i] - rectangle_size[1] // 2),
                        height=rectangle_size[0],
                        width=rectangle_size[1],
                        angle=0)
        e.set_facecolor('none')
        e.set_edgecolor(color)
        e.set_alpha(0.7)
        e.set_linewidth(1.3)
        ax1.add_artist(e)
    if ax is not None:
        return ax

def display_scarlet_model(blend, images, observation, show_ind=None, stretch=2, Q=1, minimum=0.0, channels='grizy', show_mark=True):
    from scarlet.display import AsinhMapping
    import scarlet
    # Sometimes we only want to show a few sources
    if show_ind is not None:
        sources = np.copy(blend.sources)
        gal_sources = np.array(sources)[show_ind]
        blend = scarlet.Blend(gal_sources, observation)
    # Compute model
    model = blend.get_model()  # this model is under `model_frame`, i.e. under the modest PSF
    # Render it in the observed frame
    model_ = observation.render(model)
    # Compute residual
    residual = images - model_

    # Create RGB images
    norm = AsinhMapping(minimum=minimum, stretch=stretch, Q=Q)
    img_rgb = scarlet.display.img_to_rgb(images, norm=norm)
    channel_map = scarlet.display.channels_to_rgb(len(channels))
    model_rgb = scarlet.display.img_to_rgb(model_, norm=norm)
    norm = AsinhMapping(minimum=minimum, stretch=stretch / 2, Q=Q / 2)
    residual_rgb = scarlet.display.img_to_rgb(residual, norm=norm, channel_map=channel_map)
    vmax = np.max(np.abs(residual_rgb))

    # Show the data, model, and residual
    fig = plt.figure(figsize=(15, 5))
    ax = [fig.add_subplot(1, 3, n + 1) for n in range(3)]
    ax[0].imshow(img_rgb)
    ax[0].set_title("Data")
    ax[1].imshow(model_rgb)
    ax[1].set_title("Model")
    ax[2].imshow(residual_rgb, vmin=-vmax, vmax=vmax, cmap='seismic')
    ax[2].set_title("Residual")

    if show_mark:
        for k, src in enumerate(blend.sources):
            if isinstance(src, scarlet.source.PointSource):
                color = 'white'
            elif isinstance(src, scarlet.source.SingleExtendedSource):
                color = 'red'
            elif isinstance(src, scarlet.source.MultiExtendedSource):
                color = 'cyan'
            elif isinstance(src, scarlet.source.StarletSource):
                color = 'lime'
            else:
                color = 'yellow'
            if hasattr(src, "center"):
                y, x = src.center
                ax[0].text(x, y, k, color=color)
                ax[1].text(x, y, k, color=color)
                ax[2].text(x, y, k, color=color)
    plt.show()