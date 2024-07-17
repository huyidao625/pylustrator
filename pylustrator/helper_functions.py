#!/usr/bin/env python
# -*- coding: utf-8 -*-
# helper_functions.py

# Copyright (c) 2016-2019, Richard Gerum
#
# This file is part of Pylustrator.
#
# Pylustrator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pylustrator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pylustrator. If not, see <http://www.gnu.org/licenses/>

from __future__ import division
import matplotlib.pyplot as plt
from matplotlib.text import Text
import numpy as np
import traceback

def fig_text(x, y, text, unit="cm", *args, **kwargs):
    """
    add a text to the figure positioned in cm
    """
    fig = plt.gcf()
    if unit == "cm":
        x = x / 2.54 / fig.get_size_inches()[0]
        y = y / 2.54 / fig.get_size_inches()[1]
    if x < 0:
        x += 1
    if y < 0:
        y += 1
    return fig.text(x, y, text, picker=True, *args, **kwargs)


def add_axes(dim, unit="cm", *args, **kwargs):
    """
    add an axes with dimensions specified in cm
    """
    fig = plt.gcf()
    x, y, w, h = dim
    if unit == "cm":
        x = x / 2.54 / fig.get_size_inches()[0]
        y = y / 2.54 / fig.get_size_inches()[1]
        w = w / 2.54 / fig.get_size_inches()[0]
        h = h / 2.54 / fig.get_size_inches()[1]
    if x < 0:
        x += 1
    if y < 0:
        y += 1
    return plt.axes([x, y, w, h], *args, **kwargs)


def add_image(filename):
    plt.imshow(plt.imread(filename))
    plt.xticks([])
    plt.yticks([])


def changeFigureSize(w, h, cut_from_top=False, cut_from_left=False, fig=None):
    if fig is None:
        fig = plt.gcf()
    oldw, oldh = fig.get_size_inches()
    fx = oldw / w
    fy = oldh / h
    for axe in fig.axes:
        box = axe.get_position()
        if cut_from_top:
            if cut_from_left:
                axe.set_position([1 - (1 - box.x0) * fx, box.y0 * fy, (box.x1 - box.x0) * fx, (box.y1 - box.y0) * fy])
            else:
                axe.set_position([box.x0 * fx, box.y0 * fy, (box.x1 - box.x0) * fx, (box.y1 - box.y0) * fy])
        else:
            if cut_from_left:
                axe.set_position(
                    [1 - (1 - box.x0) * fx, 1 - (1 - box.y0) * fy, (box.x1 - box.x0) * fx, (box.y1 - box.y0) * fy])
            else:
                axe.set_position([box.x0 * fx, 1 - (1 - box.y0) * fy, (box.x1 - box.x0) * fx, (box.y1 - box.y0) * fy])
    for text in fig.texts:
        x0, y0 = text.get_position()
        if cut_from_top:
            if cut_from_left:
                text.set_position([1 - (1- x0) * fx, y0 * fy])
            else:
                text.set_position([x0 * fx, y0 * fy])
        else:
            if cut_from_left:
                text.set_position([1 - (1 - x0) * fx, 1 - (1 - y0) * fy])
            else:
                text.set_position([x0 * fx, 1 - (1 - y0) * fy])
    fig.set_size_inches(w, h, forward=True)


def loadFigureFromFile(filename, fig1=None):
    from pylustration import changeFigureSize
    import os, sys
    from importlib import import_module
    from matplotlib import _pylab_helpers
    import pylustration

    # defaults to the current figure
    if fig1 is None:
        fig1 = plt.gcf()

    class noShow:
        """
        An environment that prevents the script from calling the plt.show function
        """
        def __enter__(self):
            # store the show function
            self.show = plt.show
            self.dragger = pylustration.StartDragger

            # define an empty function
            def empty(*args, **kwargs):
                pass

            # set the show function to the empty function
            plt.show = empty
            pylustration.StartDragger = empty

        def __exit__(self, type, value, traceback):
            # restore the old show function
            plt.show = self.show
            pylustration.StartDragger = self.dragger

    class noNewFigures:
        """
        An environment that prevents the script from creating new figures in the figure manager
        """
        def __enter__(self):
            # reset the figure manangar and store the current state
            self.fig = _pylab_helpers.Gcf.figs
            self.active = _pylab_helpers.Gcf._activeQue
            _pylab_helpers.Gcf.figs = {}
            _pylab_helpers.Gcf._activeQue = []

        def __exit__(self, type, value, traceback):
            # reset the figure manager
            _pylab_helpers.Gcf.figs = self.fig
            _pylab_helpers.Gcf._activeQue = self.active

    with noNewFigures():
        # prevent the script we want to load from calling show
        with noShow():
            # add the path of the sys.path
            sys.path.insert(0, os.path.dirname(os.path.abspath(filename)))
            # import the filename
            import_module(os.path.basename(filename))
            # remove the path from sys.path
            sys.path.pop(0)
        fig2 = plt.gcf()

    # get the size of the old figure
    w1, h1 = fig1.get_size_inches()
    # get the size of the new figure
    w2, h2 = fig2.get_size_inches()

    # calculate the size of the joined figure
    w = np.max([w1, w2])
    h = h1+h2

    # change the sizes of the two figures
    changeFigureSize(w, h, fig=fig1)
    changeFigureSize(w, h, cut_from_top=True, fig=fig2)

    # move the axes from the new figure to the old figure
    for index, ax in enumerate(fig2.axes):
        fig1._axstack.add(fig1._make_key(ax), ax)
        ax.figure = fig1
        fig2.delaxes(ax)


def mark_inset(parent_axes, inset_axes, loc1=1, loc2=2, **kwargs):
    from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxPatch, BboxConnector
    try:
        loc1a, loc1b = loc1
    except:
        loc1a = loc1
        loc1b = loc1
    try:
        loc2a, loc2b = loc2
    except:
        loc2a = loc2
        loc2b = loc2
    rect = TransformedBbox(inset_axes.viewLim, parent_axes.transData)

    pp = BboxPatch(rect, fill=False, **kwargs)
    parent_axes.add_patch(pp)
    pp.set_clip_on(False)

    p1 = BboxConnector(inset_axes.bbox, rect, loc1=loc1a, loc2=loc1b, **kwargs)
    inset_axes.add_patch(p1)
    p1.set_clip_on(False)
    p2 = BboxConnector(inset_axes.bbox, rect, loc1=loc2a, loc2=loc2b, **kwargs)
    inset_axes.add_patch(p2)
    p2.set_clip_on(False)

    return pp, p1, p2


def draw_from_point_to_bbox(parent_axes, insert_axes, point, loc=1, **kwargs):
    from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxConnector, Bbox
    rect = TransformedBbox(Bbox([point, point]), parent_axes.transData)
    # rect = TransformedBbox(Bbox([[1, 0], [1, 0]]), parent_axes.transData)
    p1 = BboxConnector(rect, insert_axes.bbox, loc, **kwargs)
    parent_axes.add_patch(p1)
    p1.set_clip_on(False)
    return p1


def draw_from_point_to_point(parent_axes, insert_axes, point1, point2, **kwargs):
    from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxConnector, Bbox
    rect = TransformedBbox(Bbox([point1, point1]), parent_axes.transData)
    rect2 = TransformedBbox(Bbox([point2, point2]), insert_axes.transData)
    # rect = TransformedBbox(Bbox([[1, 0], [1, 0]]), parent_axes.transData)
    loc = 1
    p1 = BboxConnector(rect, rect2, loc, **kwargs)
    parent_axes.add_patch(p1)
    p1.set_clip_on(False)
    return p1


def mark_inset_pos(parent_axes, inset_axes, loc1, loc2, point, **kwargs):
    kwargs["lw"] = 0.8
    ax_new = plt.axes(inset_axes.get_position())
    ax_new.set_xlim(point[0], point[0])
    ax_new.set_ylim(point[1], point[1])
    mark_inset(parent_axes, ax_new, loc1, loc2, **kwargs)
    plt.xticks([])
    plt.yticks([])
    ax_new.set_zorder(inset_axes.get_zorder() - 1)


def VoronoiPlot(points, values, vmin=None, vmax=None, cmap=None):
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    from scipy.spatial import Voronoi, voronoi_plot_2d
    from matplotlib import cm

    if cmap is None:
        cmap = cm.get_cmap('viridis')

    vor = Voronoi(points)

    # %%
    patches = []
    dist_list = []
    excluded_indices = []
    for index, p in enumerate(points):
        # print(index)
        reg = vor.regions[vor.point_region[index]]
        if -1 in reg:
            # plt.plot(p[0], p[1], 'ok', alpha=0.3, ms=1)
            excluded_indices.append(index)
            continue
        distances = np.linalg.norm(np.array([vor.vertices[i] for i in reg]) - p, axis=1)
        if np.max(distances) > 2:
            # plt.plot(p[0], p[1], 'ok', alpha=0.3, ms=1)
            excluded_indices.append(index)
            continue
        region = np.array([vor.vertices[i] for i in reg])
        polygon = Polygon(region, True)
        patches.append(polygon)
        dists = values[index]
        dist_list.append(dists)
        # plt.plot(p[0], p[1], 'ok', alpha=0.3, ms=1)

    p = PatchCollection(patches, cmap=cmap)
    p.set_clim([vmin, vmax])
    p.set_array(np.array(dist_list))
    p.set_linewidth(10)

    plt.gca().add_collection(p)
    plt.xticks([])
    plt.yticks([])
    return p, excluded_indices


def selectRectangle(axes=None):
    if axes is None:
        axes = plt.gca()

    def onselect(eclick, erelease):
        'eclick and erelease are matplotlib events at press and release'
        print(' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata))
        print(' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata))
        print(' used button   : ', eclick.button)

    from matplotlib.widgets import RectangleSelector
    rect_selector = RectangleSelector(axes, onselect)
    return rect_selector


def despine(ax=None, complete=False):
    if not ax:
        ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    if complete:
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # Only show ticks on the left and bottom spines
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')



letter_index = 0
def add_letter(ax = None, offset=0, offset2=0, letter=None):
    global letter_index
    from matplotlib.transforms import Affine2D, ScaledTranslation

    # get the axes
    if ax is None:
        ax = plt.gca()

    # get the figure
    fig = ax.figure

    # get the font properties for figure letters
    font = get_letter_font_prop()

    # if no letter is given
    if letter is None:
        # use the letter_format from the font
        letter = font.letter_format
        # and add a letter given the current letter_index
        letter = letter.replace("a", chr(ord("a") + letter_index))
        letter = letter.replace("A", chr(ord("A") + letter_index))
        # increase the letter index
        letter_index += 1

    # add a transform that gives the coordinates relative to the left top corner of the axes in cm
    transform = Affine2D().scale(1 / 2.54, 1 / 2.54) + fig.dpi_scale_trans + ScaledTranslation(0, 1, ax.transAxes)

    # add a text a the given position
    ax.text(-0.5+offset, offset2, letter, fontproperties=font, transform=transform, ha="center", va="bottom", picker=True)

def get_letter_font_prop():
    from matplotlib.font_manager import FontProperties
    font = FontProperties()
    font.set_family("C:\\WINDOWS\\Fonts\\HelveticaNeue-CondensedBold.ttf")
    font.set_weight("heavy")
    font.set_size(10)
    font.letter_format = "a"
    return font

def add_letters(*args, **kwargs):
    for ax in plt.gcf().axes:
        add_letter(ax, *args, **kwargs)

def axes_to_grid(axes=None, track_changes=False):
    # get the axes list
    if axes is None:
        fig = plt.gcf()
        axes = fig.axes
    if len(axes) == 0:
        return

    # get width and heights
    width = np.mean([ax.get_position().width for ax in axes])
    height = np.mean([ax.get_position().height for ax in axes])
    dims = [width, height]

    # group the axes to positions on a grid
    pos = [[], []]
    axes_indices = []
    for ax in axes:
        center = np.mean(ax.get_position().get_points(), axis=0)
        new_indices = [0, 0]
        for i in [0, 1]:
            d = np.abs(pos[i] - center[i])
            if len(d) == 0 or np.min(d) > dims[i]/2:
                pos[i].append(center[i])
                new_indices[i] = len(pos[i])-1
            else:
                new_indices[i] = np.argmin(d)
        axes_indices.append(new_indices)
    # sort the indices
    for i in [0, 1]:
        sorted_indices = np.argsort(pos[i], axis=0)
        for indices in axes_indices:
            indices[i] = sorted_indices[indices[i]]

    # the count of plots
    x_count = np.max([i[0] for i in axes_indices])
    y_count = np.max([i[1] for i in axes_indices])

    # extent of the whole plot area
    x_min = np.min([ax.get_position().get_points()[0][0] for ax in axes])
    x_max = np.max([ax.get_position().get_points()[1][0] for ax in axes])
    y_min = np.min([ax.get_position().get_points()[0][1] for ax in axes])
    y_max = np.max([ax.get_position().get_points()[1][1] for ax in axes])

    # the space between plots
    if x_count == 0:
        x_gap = 0
    else:
        x_gap = ((x_max-x_min)-(x_count+1)*width)/x_count
    if y_count == 0:
        y_gap = 0
    else:
        y_gap = ((y_max-y_min)-(y_count+1)*height)/y_count

    # make all the plots the same size and align them on the grid
    for i, ax in enumerate(axes):
        ax.set_position([x_min+axes_indices[i][0] * (width+x_gap),
                        y_min+axes_indices[i][1] * (height + y_gap),
                        width,
                        height,
                        ])
        if track_changes is True:
            ax.figure.change_tracker.addChange(ax, ".set_position([%f, %f, %f, %f])" % (x_min+axes_indices[i][0] * (width+x_gap), y_min+axes_indices[i][1] * (height + y_gap), width, height))

    # make all the plots have the same limits
    xmin = np.min([ax.get_xlim()[0] for ax in axes])
    xmax = np.max([ax.get_xlim()[1] for ax in axes])
    ymin = np.min([ax.get_ylim()[0] for ax in axes])
    ymax = np.max([ax.get_ylim()[1] for ax in axes])
    for ax in axes:
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

    # hide ticks and labels on plots that are not on the left or bottom
    for i, ax in enumerate(axes):
        if axes_indices[i][0] != 0:
            ax.set_ylabel("")
            ax.set_yticklabels([])
            if track_changes is True:
                ax.figure.change_tracker.addChange(ax, ".get_yaxis().get_label().set_text('')")
                ax.figure.change_tracker.addChange(ax, ".set_yticklabels([])")
        if axes_indices[i][1] != 0:
            ax.set_xlabel("")
            ax.set_xticklabels([])
            if track_changes is True:
                ax.figure.change_tracker.addChange(ax, ".get_xaxis().get_label().set_text('')")
                ax.figure.change_tracker.addChange(ax, ".set_xticklabels([])")
        despine(ax)
        if track_changes is True:
            ax.figure.change_tracker.addChange(ax, ".spines['right'].set_visible(False)")
            ax.figure.change_tracker.addChange(ax, ".spines['top'].set_visible(False)")

def main_figure(artist):
    if artist is None:
        return None
    if artist.figure == artist:
        return artist
    else:
        return main_figure(artist.figure)