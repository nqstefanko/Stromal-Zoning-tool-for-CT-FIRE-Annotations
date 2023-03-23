from PIL import Image, ImageDraw, ImageFont, ImageColor
from datetime import datetime
from numpyencoder import NumpyEncoder
from pprint import pprint
from scipy.io import loadmat
from termcolor import cprint, colored

import functools
import geojson
import geopandas
import json
import math
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import pathlib
import shapely.geometry as geo # Polygon, Point
import shapely.affinity as aff
import time
import traceback

from ctfire_output_helper import CTFIREOutputHelper
from annotation_helper import AnnotationHelper
from shapely.plotting import plot_polygon

# https://stackoverflow.com/questions/57657419/how-to-draw-a-figure-in-specific-pixel-size-with-matplotlib

# #CROPPED_IMG DATA
# TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.tif"
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout\ctFIREout_2B_D9_crop2.mat"

#16 DENOISED DATA 16
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-016_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-016_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\ctFIREout\ctFIREout_DCIS-016_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

# #18 DENOISED DATA 18
EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-018_10x10_1_Nuclei_Collagen - Denoised.geojson")
TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-018_10x10_1_Nuclei_Collagen - Denoised.tif")
MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\ctFIREout_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

with Image.open(TIF_FILEPATH) as img:
    IMG_DIMS = img.size

def print_function_dec(func):
    """This function is written to help write out time of functions and get exceptions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(colored("Going into ", 'magenta') + colored(func.__name__, 'green') + colored(f" at time {datetime.utcnow()}", "magenta"))
        try:
            result = func(*args, **kwargs)
            print(colored("Done with ", 'magenta') + colored(func.__name__, 'green') + colored(f" at time {datetime.utcnow()}", "magenta"))
            return result
        except Exception as e:
            cprint(f"Caught an exception at {func.__name__}: '{str(e)}'", "red")
            traceback.print_exc()
    return wrapper

class DrawingHelper():
    def __init__(self, ctf_helper=None, anno_helper=None, tif_file=None) -> None:
        self.annotation_helper_obj = anno_helper 
        self.ctf_output_obj  = ctf_helper
        self.tif_file = tif_file
        self.rgbimg =  self._convert_grayscale_tif_to_color()
        self.draw_image = ImageDraw.Draw(self.rgbimg)

    def _convert_grayscale_tif_to_color(self):
        self.image = Image.open(self.tif_file, 'r').convert('RGBA')
        rgbimg = Image.new("RGBA", self.image.size)
        rgbimg.paste(self.image)
        return rgbimg

    def _draw_annotations(self,  final_path_to_save=None, draw_anno_indexes=False):
        font = ImageFont.truetype("arial.ttf", 25)
        for i, annotation in enumerate(self.annotation_helper_obj.annotations):
            poly = annotation.geo_polygon
            x, y = poly.exterior.xy
            flat_points2 = np.stack((x, y), axis=1).flatten()
            self.draw_image.line(flat_points2.astype(np.float32), width=15, fill=tuple(annotation.color), joint='curve')

            if draw_anno_indexes:
                xcent = poly.centroid.coords.xy[0][0]
                ycent = poly.centroid.coords.xy[1][0]
                self.draw_image.text([xcent, ycent], f"Ind: {i}", font=font)

        if(final_path_to_save):
            composite_image = Image.alpha_composite(self.image, self.rgbimg)
            composite_image.save(final_path_to_save)

    def draw_fibers(self, final_path_to_save=None):
        verts = self.ctf_output_obj.get_fiber_vertices_thresholded()
        widths = self.ctf_output_obj.get_fiber_widths_thresholded()
        for i in range(len(verts)):
            # to_add:to_add+5 - print(i, ctf_output.centeroidnp(verts[i + to_add][:, 0], verts[i + to_add][:, 1]))
            self.draw_image.line(verts[i].flatten().astype(np.float32),
                                 width=int(round(widths[i])),
                                 fill=tuple(np.random.choice(range(256), size=3)),
                                 joint="curve")

        if(final_path_to_save):
            composite_image = Image.alpha_composite(self.image, self.rgbimg)
            composite_image.save(final_path_to_save)
    
    def draw_zones(self, zones=[0, 50, 150], to_draw=[0, 1, 2, 3], final_path_to_save=None):
        colors = ['orange', 'green', 'magenta', 'red']
        list_of_union_zones =  list(reversed(self.annotation_helper_obj.get_final_zones(zones)))
        
        for i in range(len(list_of_union_zones)):
            # 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself
            if(i in to_draw):
                final_union_zone_polygon = list_of_union_zones[i]
                print(i, f'{final_union_zone_polygon.area:,}', colors[i])
                # verts = final_union_zone_polygon.exterior.coords
                for polygon in final_union_zone_polygon.geoms:
                    coords = np.array(polygon.exterior.coords).astype('float32')
                    filling = ImageColor.getrgb(colors[i]) + (64,)
                    lining = ImageColor.getrgb(colors[i]) + (128,)
                    self.draw_image.polygon(coords, width=10, fill=filling, outline=lining)

        if(final_path_to_save):
            
            final_path = os.path.join(sys.path[0], final_path_to_save)
            composite_image = Image.alpha_composite(self.image, self.rgbimg)
            composite_image.save(final_path)
         
        return list_of_union_zones
        
    @print_function_dec
    def save_final_overlay(self, anno_on_top=True, with_zones=False, final_path_to_save='bong_overlayed.tif'):
        if with_zones:
            self.draw_zones()
            
        if anno_on_top:
            self.draw_fibers()
            self._draw_annotations()
        else:
            self._draw_annotations()
            self.draw_fibers()

        final_path = os.path.join(sys.path[0], final_path_to_save)
        composite_image = Image.alpha_composite(self.image, self.rgbimg)
        composite_image.save(final_path)
        return final_path
 
    @print_function_dec
    def draw_fibers_per_zone(self, bucketed_fibers, to_draw = [0, 1, 2, 3]):
        verts = self.ctf_output_obj.get_fiber_vertices_thresholded()
        widths = self.ctf_output_obj.get_fiber_widths_thresholded()
        
        labeled_fibers = bucketed_fibers.min(axis=1)
        for bucket in to_draw:
            indexes_to_plot = np.where(labeled_fibers == bucket)[0]
            for i in indexes_to_plot:
                self.draw_image.line(verts[i].flatten().astype(np.float32), width=int(round(widths[i])), fill=tuple(np.random.choice(range(256), size=3)), joint="curve")

    @print_function_dec
    def reset(self, new_tif):
        self.new_tif = new_tif
        self.rgbimg =  self._convert_grayscale_tif_to_color()
        self.draw_image = ImageDraw.Draw(self.rgbimg)

class PlottingHelper():
    """This class is written to help the plotting of fibers, annotations, and zones over a tif file"""
    def __init__(self, ctf_helper=None, anno_helper=None, tif_file=None) -> None:
        self.annotation_helper_obj = anno_helper 
        self.ctf_output_obj  = ctf_helper
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.tif_file = tif_file
        self.img = None
        self.img_dims = None
        if(tif_file):
            self.set_img(tif_file)

    def set_img(self, tif_file):
        self.img = plt.imread(tif_file)
        img_width = self.img.shape[0]
        img_height = self.img.shape[1]
        self.img_dims = (img_width, img_height) 
        # im = self.ax.imshow(self.img, cmap='gray', extent=[0, img_width+10, 0, img_height+10])
        im = self.ax.imshow(self.img, cmap='gray', extent=[0, img_width, 0, img_height])
        
    def _rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def _plot_annotations(self, annotations_to_plot=[], plot_anno_indexes=False):
        for i, annotation in enumerate(self.annotation_helper_obj.annotations):
            if(len(annotations_to_plot) == 0 or annotation.name in annotations_to_plot):
                original_annotation_poly = annotation.geo_polygon
                x, y = original_annotation_poly.exterior.xy
                
                # Fixes y to adjust to 0,0 in bottom left for plot (not 0,0 top left for image)
                y_points = np.abs(np.array(y) - self.img_dims[1]) 
                stacked = np.column_stack((x, y_points))
                fixed_y_annotation_poly = geo.Polygon(stacked)
                plot_polygon(fixed_y_annotation_poly, self.ax, add_points = False, fill=False, linewidth = 4, alpha=1, 
                        color=self._rgb_to_hex(tuple(annotation.color)))
                
                # If for debugging you want to plot the indexes of each annotation
                if plot_anno_indexes:
                    xcent = fixed_y_annotation_poly.centroid.coords.xy[0][0]
                    ycent = fixed_y_annotation_poly.centroid.coords.xy[1][0]
                    self.ax.text(xcent, ycent, f'{i, annotation.name}', fontsize=12, color='orange')
    
    def _plot_zones(self, zones=[0, 50, 150], to_plot=[0, 1, 2, 3]):
        colors = ['orange', 'green', 'magenta', 'red']
        list_of_union_zones =  list(reversed(self.annotation_helper_obj.get_final_zones_for_plotting(zones, self.ax)))
        
        for i in range(len(list_of_union_zones)):
            # 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself
            if(i in to_plot):
                final_union_zone_polygon = list_of_union_zones[i]
                print(i, f'{final_union_zone_polygon.area:,}', colors[i])
                plot_polygon(final_union_zone_polygon, self.ax, add_points = False, fill=True, linewidth = 2, alpha=.55, color=colors[i])
        return list_of_union_zones

    def _plot_fibers(self, thresholded = True):
        verts = self.ctf_output_obj.get_fiber_vertices_thresholded()
        if not thresholded:
            verts = self.ctf_output_obj.get_all_fiber_vertices()
            
        for i in range(len(verts)):
            x_points = verts[i][:, 0]
            y_points = np.abs(verts[i][:, 1].astype('int16') - self.img_dims[1])
            self.ax.plot(x_points, y_points, linestyle="-")
    
    def _plot_fibers_per_zone(self, bucketed_fibers, to_plot = [0, 1, 2, 3]):
        verts = self.ctf_output_obj.get_fiber_vertices_thresholded()
        
        labeled_fibers = bucketed_fibers.min(axis=1)
        for bucket in to_plot:
            indexes_to_plot = np.where(labeled_fibers == bucket)[0]
            for i in indexes_to_plot:
                x_points = verts[i][:, 0]
                y_points = np.abs(verts[i][:, 1].astype('int16') - self.img_dims[1])
                self.ax.plot(x_points, y_points, linestyle="-")

    @print_function_dec
    def plot_final_overlay(self, save_plot_as_img=None):
        self._plot_fibers()
        
        self._plot_annotations()
        
        if(save_plot_as_img):
            cprint(f'Saving plot to file: {save_plot_as_img}', 'cyan')
            self.ax.set_frame_on(False)
            self.ax.axes.get_xaxis().set_visible(False)
            self.ax.axes.get_yaxis().set_visible(False)
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
            plt.margins(0,0)
            plt.tight_layout()
            plt.savefig(save_plot_as_img, bbox_inches='tight',  pad_inches = 0, dpi=300)

    def show_plot(self):
        self.fig.show()
        plt.show()
        plt.close(self.fig)
        
    def reset(self, new_tif=None):
        self.fig = plt.figure(1)
        self.ax = plt.axes()
        if new_tif is not None:
            self.tif_file = new_tif
        self.set_img(self.tif_file )

    def close_plot(self):
        plt.close() 
        
@print_function_dec
def bucket_the_fibers(ctf_helper_obj, annotation_helper_obj, buckets=np.array([0, 50, 150])):
    """Buckets Each fiber into an annotation for every annotation"""
    # Return Arr (len fibers, len anno) - For each fibers, we have an array for each annotation with represented bucket.
    fibers = ctf_helper_obj.get_fiber_vertices_thresholded()
    centroids = ctf_helper_obj.get_centroids()

    shape = (len(fibers), len(annotation_helper_obj.annotations))
    fibers_bucketed = np.ones(shape, dtype=int)
    for i, centroid in enumerate(centroids):
        centroid_x = centroid[0]
        centroid_y = centroid[1]
        centroid_point = geo.Point(centroid_x, centroid_y)
        fiber_linestring = geo.LineString(fibers[i])

        poly_distances = np.array(range(len(annotation_helper_obj.annotations)))
        for j, annotation in enumerate(annotation_helper_obj.annotations):
            g_poly = annotation.geo_polygon
            poly_distances[j] = g_poly.exterior.distance(centroid_point)
            
            if (g_poly.contains(centroid_point) or g_poly.contains(fiber_linestring)):  # Could use fiber_linestring but much more restrictive
                poly_distances[j] = -1

            if(fiber_linestring.crosses(g_poly)):
                poly_distances[j] = 1
        bucket_fibers = np.digitize(poly_distances, buckets, right=True).astype(int)
        fibers_bucketed[i] = bucket_fibers
    return fibers_bucketed
    # return fibers_bucketed[0:len(centroids)]

@print_function_dec
def get_signal_density_per_annotation(annotation_helper_obj, bucketed_fibers = None, zones = np.array([50, 150])):
    total_area, stromal_area, anno_area, stromal_percentage, annotation_percentage = get_annotation_areas(annotation_helper_obj)
    final_areas = {0:0, 1:0, 2:0}
    final_counts = {0:0, 1:0, 2:0, 3:0}

    lengths = ctf_output.get_fiber_lengths_thresholded()
    widths = ctf_output.get_fiber_widths()
    
    for i, poly in enumerate(annotation_helper_obj.geo_polygons):
        epith_zone = poly.buffer(50, single_sided=True)
        medium_zone = poly.buffer(150, single_sided=True)        
        final_areas[0]+= poly.area
        final_areas[1]+= (epith_zone.area - poly.area)
        final_areas[2]+= (medium_zone.area -  epith_zone.area) 
    
    labeled_fibers = bucketed_fibers.min(axis=1)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for i in range(len(bucketed_fibers)):
        final_counts[labeled_fibers[i]] +=  lengths[i] * widths[i]
    
    cprint(f"Non-Stromal Area: {final_areas[0]}", 'cyan')
    cprint(f"Eptih Area: {final_areas[1]}", 'green')
    cprint(f"Mid Area: {final_areas[2]}", 'cyan')
    cprint(f"Stromal Area: {3700**2 - final_areas[0] - final_areas[1] - final_areas[2]}", 'green')
    cprint(f"Total: {stromal + final_areas[2]} is equal to {3700**2}", 'cyan')
    
    print("Non-Stromal:", final_counts[0] / final_areas[0])
    print("Epithelial:", final_counts[1] / final_areas[1])
    print("Mid:", final_counts[2] / final_areas[2])
    print("Stromal:", final_counts[3] / stromal)

def get_signal_density_overall(ctf_output_obj, annotation_helper_obj, bucketed_fibers = None, buckets = None, zones = np.array([50, 150])):
    # This is the current 4 zones bro
    lengths = ctf_output_obj.get_fiber_lengths_thresholded()
    widths = ctf_output_obj.get_fiber_widths_thresholded()
    
    #FOR BUCKETED FIBERS:  0 is annotation, 1 is epith, 2 is mid, 3 is stromal

    labeled_fibers = bucketed_fibers.min(axis=1)
    # actual_counts = {0: 0, 1: 0, 2: 0, 3: 0} 
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for i in range(len(bucketed_fibers)):
        final_counts[labeled_fibers[i]] +=  lengths[i] * widths[i]
        # actual_counts[labeled_fibers[i]] +=  1
    
    #For Final Union of Zones, it is reversed: 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself. So we reverse it
    final_densities = []
    final_union_of_zones = annotation_helper_obj.get_final_zones([0, 50, 150]) 
    for i, zone in enumerate(reversed(final_union_of_zones)):
        # print(f"Zone {len(final_union_of_zones) - i - 1}: {zone.area}")
        final_densities.append(final_counts[len(final_union_of_zones) - i - 1] / zone.area)

    return final_densities

def get_average_width_per_zone(ctf_output_obj, bucketed_fibers):
    labeled_fibers = bucketed_fibers.min(axis=1)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    widths = ctf_output_obj.get_fiber_widths()

    for i in range(4):
        labeled_widths = widths[np.where(labeled_fibers == i)]
        if(not labeled_widths.any()):
            width_mean = 0
        else:
            width_mean =  np.mean(labeled_widths)
        final_counts[i] = width_mean 

    return final_counts

def get_average_length_per_zone(ctf_output_obj, bucketed_fibers):
    labeled_fibers = bucketed_fibers.min(axis=1)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    lengths = ctf_output_obj.get_fiber_lengths_thresholded()

    for i in range(4):
        labeled_lengths = lengths[np.where(labeled_fibers == i)]
        if(not labeled_lengths.any()):
            width_mean = 0
        else:
            width_mean =  np.mean(labeled_lengths)
        final_counts[i] = width_mean 

    return final_counts

def get_average_angle_per_zone(ctf_output_obj, bucketed_fibers):
    labeled_fibers = bucketed_fibers.min(axis=1)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    angles = ctf_output_obj.get_fiber_angles()
    
    for i in range(4):
        labeled_angles = angles[np.where(labeled_fibers == i)]
        if(not labeled_angles.any()):
            width_mean = 0
        else:
            width_mean =  np.mean(labeled_angles)
        final_counts[i] = width_mean 

    return final_counts

if __name__ == '__main__':
    pass


