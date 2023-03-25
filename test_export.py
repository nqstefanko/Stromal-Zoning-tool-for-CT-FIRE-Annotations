from PIL import Image, ImageDraw, ImageFont, ImageColor
from datetime import datetime
from numpyencoder import NumpyEncoder
from pprint import pprint
from scipy.io import loadmat
from termcolor import cprint, colored
import shapely
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

COLORS = ['cyan', 'green', 'magenta', 'red', 'yellow', 'blue', 'white', 'orange', 'pink', 'brown']
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
    def __init__(self, tif_file=None) -> None:
        self.tif_file = tif_file
        self.rgbimg =  self._convert_grayscale_tif_to_color()
        self.draw_image = ImageDraw.Draw(self.rgbimg)
    def _draw_polygon_helper(self, polygon, color):
        "NOTE: TECHNICALLY THIS IS NOT CORRECT YET BECAUSE DRAWING OVER WITH ALPHA 0 STILL DRAWS OVER WHAT IS THERE."
        if type(polygon.boundary) == shapely.geometry.MultiLineString:
            if len(polygon.boundary.geoms) > 0:
                filling = ImageColor.getrgb(color) + (32,)
                lining = ImageColor.getrgb(color) + (64,)
                geom = polygon.boundary.geoms[0]
                coords =  geom.coords.xy[0]
                ext_x_coords = np.array(polygon.boundary.geoms[0].coords.xy[0]).astype('float32')
                ext_y_coords = np.array(polygon.boundary.geoms[0].coords.xy[1]).astype('float32')
                final_ext = np.vstack((ext_x_coords, ext_y_coords)).T.flatten()
                print(f"Drawing Multiline Polygon: {color}")
                self.draw_image.polygon(final_ext, width=5, fill=filling, outline=lining)

                for i in range(len(polygon.boundary.geoms)-1):
                    geo = polygon.boundary.geoms[i+1]
                    int_x_coords = np.array(geo.coords.xy[0]).astype('float32')
                    int_y_coords = np.array(geo.coords.xy[1]).astype('float32')
                    final_int = np.vstack((int_x_coords, int_y_coords)).T.flatten()
                    print(f"ERASING Multiline Polygon: {color}")
                    self.draw_image.polygon(final_int, width=5, outline=lining, fill=(255, 255, 255, 0))
                
        else:
            print(f"Drawing Polygon: {color}")
            coords = np.array(polygon.exterior.coords).astype('float32')
            filling = ImageColor.getrgb(color) + (32,)
            lining = ImageColor.getrgb(color) + (64,)
            self.draw_image.polygon(coords, width=5, fill=filling, outline=lining)
    
    def _draw_helper(self, final_union_poly, color):
        if(type(final_union_poly) == shapely.geometry.multipolygon.MultiPolygon):
            for polygon in final_union_poly.geoms:
                self._draw_helper(polygon, color)
        else:
            self._draw_polygon_helper(final_union_poly, color) 

    
    def draw_zones(self, list_of_union_zones, to_draw=[],  colors = COLORS):
        list_to_draw = list(to_draw)
        # for i in range(len(list_of_union_zones)):
        for i in reversed(range(len(list_of_union_zones))):
            # 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself
            if((not list_to_draw or i in list_to_draw) and list_of_union_zones[i].area > 0):
                final_union_zone_polygon = list_of_union_zones[i]
                cprint(f"{i, f'{final_union_zone_polygon.area:,}', colors[i]}", colors[i])
                self._draw_helper(final_union_zone_polygon, colors[i]) 
        self.image = Image.alpha_composite(self.image, self.rgbimg)
            
    def _convert_grayscale_tif_to_color(self):
        self.image = Image.open(self.tif_file, 'r').convert('RGBA')
        rgbimg = Image.new("RGBA", self.image.size)
        rgbimg.paste(self.image)
        return rgbimg

    def draw_annotations(self, annos_to_draw, draw_anno_indexes=False):
        font = ImageFont.truetype("arial.ttf", 25)
        for annotation in annos_to_draw:
            poly = annotation.geo_polygon
            x, y = poly.exterior.xy
            flat_points2 = np.stack((x, y), axis=1).flatten()
            self.draw_image.line(flat_points2.astype(np.float32), width=10, fill=tuple(annotation.color), joint='curve')

            if draw_anno_indexes:
                xcent = poly.centroid.coords.xy[0][0]
                ycent = poly.centroid.coords.xy[1][0]
                self.draw_image.text([xcent, ycent], f"Ind: {annotation.original_index}", font=font)
        self.image = Image.alpha_composite(self.image, self.rgbimg)

    def draw_fibers(self, verts, widths):
        for i in range(len(verts)):
            # to_add:to_add+5 - print(i, ctf_output.centeroidnp(verts[i + to_add][:, 0], verts[i + to_add][:, 1]))
            self.draw_image.line(
                verts[i].flatten().astype(np.float32),
                width=int(round(widths[i])),
                fill=tuple(np.random.choice(range(256), size=3)),
                joint="curve"
            )
        
        self.image = Image.alpha_composite(self.image, self.rgbimg)
        
        
    @print_function_dec
    def draw_overlay(self, draw_functions):
        for draw_function in draw_functions:
            draw_function()

    def get_image(self):
        return Image.alpha_composite(self.image, self.rgbimg)

    def save_file_overlay(self, final_path_to_save='bong_overlayed.tif'):
        final_path = os.path.join(sys.path[0], final_path_to_save)
        composite_image = Image.alpha_composite(self.image, self.rgbimg)
        composite_image.save(final_path)
        return final_path
 
    @print_function_dec
    def draw_fibers_per_zone(self, verts, widths, bucketed_fibers, to_draw = [0, 1, 2, 3]):
        labeled_fibers = bucketed_fibers.min(axis=1)
        for bucket in to_draw:
            indexes_to_plot = np.where(labeled_fibers == bucket)[0]
            for i in indexes_to_plot:
                self.draw_image.line(verts[i].flatten().astype(np.float32), width=int(round(widths[i])), fill=tuple(np.random.choice(range(256), size=3)), joint="curve")
        self.image = Image.alpha_composite(self.image, self.rgbimg)

    @print_function_dec
    def reset(self, new_tif=None):
        if(new_tif):
            self.tif_file = new_tif
        self.rgbimg =  self._convert_grayscale_tif_to_color()
        self.draw_image = ImageDraw.Draw(self.rgbimg)

class PlottingHelper():
    """This class is written to help the plotting of fibers, annotations, and zones over a tif file"""
    def __init__(self, tif_file=None) -> None:
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

    def _plot_annotations(self, annotations_to_plot,  plot_anno_indexes=False):
        for annotation in annotations_to_plot:
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
                self.ax.text(xcent, ycent, f'{annotation.original_index, annotation.name}', fontsize=12, color='orange')
    
    def _plot_zones(self, list_of_union_zones, to_plot=[], colors = COLORS):
        for i in range(len(list_of_union_zones)):
            # 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself
            if((not to_plot or i in to_plot) and list_of_union_zones[i].area > 0):
                final_union_zone_polygon = list_of_union_zones[i]
                print(i, f'{final_union_zone_polygon.area:,}', colors[i])
                plot_polygon(final_union_zone_polygon, self.ax, add_points = False, fill=True, linewidth = 2, alpha=.55, color=colors[i])
        return list_of_union_zones

    def _plot_fibers(self, verts):
        for i in range(len(verts)):
            x_points = verts[i][:, 0]
            y_points = np.abs(verts[i][:, 1].astype('int16') - self.img_dims[1])
            self.ax.plot(x_points, y_points, linestyle="-")
    
    def _plot_fibers_per_zone(self, verts, bucketed_fibers, to_plot = [0, 1, 2, 3]):
        labeled_fibers = bucketed_fibers.min(axis=1)
        for bucket in to_plot:
            indexes_to_plot = np.where(labeled_fibers == bucket)[0]
            for i in indexes_to_plot:
                x_points = verts[i][:, 0]
                y_points = np.abs(verts[i][:, 1].astype('int16') - self.img_dims[1])
                self.ax.plot(x_points, y_points, linestyle="-")

    @print_function_dec
    def plot_final_overlay(self, fibers, annotations, zones, save_plot_as_img=None):
        self._plot_zones(zones)
        self._plot_annotations(annotations)
        self._plot_fibers(fibers)
        
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

class GUI_Helper():
    def __init__(self, tif_filepath, mat_filepath, annotation_filepath) -> None:
        self.CTF_OUTPUT = CTFIREOutputHelper(mat_filepath)
        self.DRAW_HELPER = DrawingHelper(tif_filepath)
        self.ANNOTATION_HELPER = AnnotationHelper(annotation_filepath, self.DRAW_HELPER.image.size)

    @print_function_dec
    def bucket_the_fibers(self, fibers, centroids, annotations, buckets=np.array([0, 50, 150])):
        """Buckets Each fiber into an annotation for every annotation"""
        # Return Arr (len fibers, len anno) - For each fibers, we have an array for each annotation with represented bucket.

        shape = (len(fibers), len(annotations))
        fibers_bucketed = np.ones(shape, dtype=int)
        for i, centroid in enumerate(centroids):
            centroid_x = centroid[0]
            centroid_y = centroid[1]
            centroid_point = geo.Point(centroid_x, centroid_y)
            fiber_linestring = geo.LineString(fibers[i])

            poly_distances = np.array(range(len(annotations)))
            for j, annotation in enumerate(annotations):
                g_poly = annotation.geo_polygon
                poly_distances[j] = g_poly.exterior.distance(centroid_point)
                
                if (g_poly.contains(centroid_point) or g_poly.contains(fiber_linestring)):  # Could use fiber_linestring but much more restrictive
                    poly_distances[j] = -1

                if(fiber_linestring.crosses(g_poly)):
                    poly_distances[j] = 1
            bucket_fibers = np.digitize(poly_distances, buckets, right=True).astype(int)
            fibers_bucketed[i] = bucket_fibers
        self.bucketed_fibers = fibers_bucketed 
        return fibers_bucketed
        # return fibers_bucketed[0:len(centroids)]

  
@print_function_dec
def bucket_the_fibers(fibers, centroids, annotations, buckets=np.array([0, 50, 150])):
    """Buckets Each fiber into an annotation for every annotation"""
    # Return Arr (len fibers, len anno) - For each fibers, we have an array for each annotation with represented bucket.

    shape = (len(fibers), len(annotations))
    fibers_bucketed = np.ones(shape, dtype=int)
    for i, centroid in enumerate(centroids):
        centroid_x = centroid[0]
        centroid_y = centroid[1]
        centroid_point = geo.Point(centroid_x, centroid_y)
        fiber_linestring = geo.LineString(fibers[i])

        poly_distances = np.array(range(len(annotations)))
        for j, annotation in enumerate(annotations):
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
def get_signal_density_per_annotation(bucketed_fibers_annotation_indexed, annotation, lengths, widths):
    fibs_inds_in_anno = np.where(bucketed_fibers_annotation_indexed == 0)
    length_of_fibs_in_anno = lengths[fibs_inds_in_anno]
    width_of_fibs_in_anno = widths[fibs_inds_in_anno]
    final_density = np.sum(length_of_fibs_in_anno * width_of_fibs_in_anno)
    return final_density / annotation.geo_polygon.area
    
def get_fiber_area_per_zone(lengths, widths, bucketed_fibers):
    labeled_fibers = bucketed_fibers.min(axis=1)
    
    actual_counts = {0: 0, 1: 0, 2: 0, 3: 0} 
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for i in range(len(bucketed_fibers)):
        final_counts[labeled_fibers[i]] +=  lengths[i] * widths[i]
        actual_counts[labeled_fibers[i]] +=  1
    print(f"get_fiber_area_per_zone - Actual Counts: {actual_counts}")
    return final_counts

def get_signal_density_per_zone(final_union_of_zones, final_counts):
    final_densities = []
    for i, zone in enumerate(reversed(final_union_of_zones)):
        # print(f"Zone {len(final_union_of_zones) - i - 1}: {zone.area}")
        final_densities.append(final_counts[len(final_union_of_zones) - i - 1] / zone.area)
    return final_densities

def get_signal_density_overall(lengths, widths, final_union_of_zones,  bucketed_fibers):
    #FOR BUCKETED FIBERS:  0 is annotation, 1 is epith, 2 is mid, 3 is stromal
    final_counts = get_fiber_area_per_zone(lengths, widths, bucketed_fibers)

    #For Final Union of Zones, it is reversed: 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself. So we reverse it
    return get_signal_density_per_zone(final_union_of_zones, final_counts)

def get_singal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, zones):
    final_counts = get_fiber_area_per_zone(lengths, widths, bucketed_fibers)
    final_area = 0
    final_density = 0
    
    total_area = 0
    total_density = 0
    for i, zone in enumerate(reversed(final_union_of_zones)):
        zone_index = len(final_union_of_zones) - i - 1
        print(f"Zone {zone_index}: {zone.area}")
        total_area += zone.area
        total_density += final_counts[zone_index]
        
        if(zone_index in zones):
           final_area += zone.area
           final_density += final_counts[zone_index]
    
    return final_density / final_area

def get_average_width_per_zone(widths, bucketed_fibers):
    labeled_fibers = bucketed_fibers.min(axis=1)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for i in range(4):
        labeled_widths = widths[np.where(labeled_fibers == i)]
        if(not labeled_widths.any()):
            width_mean = 0
        else:
            width_mean =  np.mean(labeled_widths)
        final_counts[i] = width_mean 

    return final_counts

def get_average_length_per_zone(lengths, bucketed_fibers):
    labeled_fibers = bucketed_fibers.min(axis=1)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for i in range(4):
        labeled_lengths = lengths[np.where(labeled_fibers == i)]
        if(not labeled_lengths.any()):
            width_mean = 0
        else:
            width_mean =  np.mean(labeled_lengths)
        final_counts[i] = width_mean 

    return final_counts

def get_average_angle_per_zone(angles, bucketed_fibers):
    labeled_fibers = bucketed_fibers.min(axis=1)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    
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


# verts = final_union_zone_polygon.exterior.coords
        # overlay = Image.new('RGBA', self.image.size, (0,0,0,0))
        # draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
        # return overlay
