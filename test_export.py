from PIL import Image, ImageDraw, ImageFont
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
        image = Image.open(self.tif_file, 'r').convert('RGBA')
        rgbimg = Image.new("RGBA", image.size)
        rgbimg.paste(image)
        return rgbimg

    def _draw_annotations(self, final_path_to_save=None):
        font = ImageFont.truetype("arial.ttf", 100)
        for i, poly in enumerate(self.annotation_helper_obj.geo_polygons):
            x, y = poly.exterior.xy
            flat_points2 = np.stack((x, y), axis=1).flatten()
            self.draw_image.line(flat_points2.astype(np.float32), width=55, fill=tuple(self.annotation_helper_obj.annotation_info[i]['color']), joint='curve')

        for i, points in enumerate(self.annotation_helper_obj.points): # Separate so it goes over
            self.draw_image.text([points[0][0], points[0][1]], f"Ind: {i}", font=font)

        if(final_path_to_save):
            final_path = os.path.join(sys.path[0], final_path_to_save)
            self.draw_image._image.save(final_path)

    def draw_fibers(self):
        verts = ctf_output.get_fiber_verticies()
        widths = ctf_output.get_fiber_widths()
        for i in range(len(verts)):
        # to_add:to_add+5 - print(i, ctf_output.centeroidnp(verts[i + to_add][:, 0], verts[i + to_add][:, 1]))
            self.draw_image.line(verts[i].flatten().astype(np.float32), width=int(round(widths[i])), fill=tuple(np.random.choice(range(256), size=3)), joint="curve")
    
    @print_function_dec
    def save_final_overlay(self, on_top='A', final_path_to_save='bong_overlayed.tif'):
        if(on_top == 'A'):
            self.draw_fibers()
            self._draw_annotations()
        else:
            self._draw_annotations()
            self.draw_fibers()
        final_path = os.path.join(sys.path[0], final_path_to_save)
        self.rgbimg.save(final_path)
        return final_path
 
    @print_function_dec
    def draw_fibers_per_zone(self, bucketed_fibers, bucket = 0):
        verts = self.ctf_output_obj.get_fiber_verticies()
        widths = self.ctf_output_obj.get_fiber_widths()
        
        labeled_fibers = bucketed_fibers.min(axis=1)
        indexes_to_plot = np.where(labeled_fibers == bucket)[0]
        for i in indexes_to_plot:
            self.draw_image.line(verts[i].flatten().astype(np.float32), width=int(round(widths[i])), fill=tuple(np.random.choice(range(256), size=3)), joint="curve")

    @print_function_dec
    def reset(self, new_tif):
        self.new_tif = new_tif
        self.rgbimg =  self._convert_grayscale_tif_to_color()
        self.draw_image = ImageDraw.Draw(self.rgbimg)

class PlottingHelper():
    def __init__(self, ctf_helper=None, anno_helper=None, tif_file=None) -> None:
        self.annotation_helper_obj = anno_helper 
        self.ctf_output_obj  = ctf_helper
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.tif_file = tif_file
        if(tif_file):
            self.set_img(tif_file)

    def set_img(self, tif_file):
        self.img = plt.imread(tif_file)
        img_width = self.img.shape[0]
        img_height = self.img.shape[1]
        self.img_dims = (img_width, img_height) 
        im = self.ax.imshow(self.img, cmap='gray', extent=[0, img_width+10, 0, img_height+10])
        
    def _rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def _plot_annotations(self, img_height):
        for i, original_annotation_poly in enumerate(self.annotation_helper_obj.geo_polygons):
            x, y = original_annotation_poly.exterior.xy
            
            # Fixes y to adjust to 0,0 in bottom left for plot (not 0,0 top left for image)
            y_points = np.abs(np.array(y) - img_height) 
            stacked = np.column_stack((x, y_points))
            fixed_y_annotation_poly = geo.Polygon(stacked)
            plot_polygon(fixed_y_annotation_poly, self.ax, add_points = False, fill=False, linewidth = 2, alpha=1, 
                    color=self._rgb_to_hex(tuple(self.annotation_helper_obj.annotation_info[i]['color'])))

    def _plot_zones(self, zones, img_dimensions=(3700, 3700), to_plot=[0, 1, 2, 3]):
        colors = ['orange', 'green', 'magenta', 'red']
        list_of_union_zones =  list(reversed(self.annotation_helper_obj.get_final_zones_for_plotting(zones, self.ax, img_dimensions)))
        
        for i in range(len(list_of_union_zones)):
            # 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself
            if(i in to_plot):
                final_union_zone_polygon = list_of_union_zones[i]
                print(i, f'{final_union_zone_polygon.area:,}', colors[i])
                plot_polygon(final_union_zone_polygon, self.ax, add_points = False, fill=True, linewidth = 2, alpha=.15, color=colors[i])
        return list_of_union_zones

    def _plot_the_fibers(self, img_height=3700):
        verts = ctf_output.get_fiber_verticies()
        verts = verts[2000:2010]
        for i in range(len(verts)):
            x_points = verts[i][:, 0]
            y_points = np.abs(verts[i][:, 1].astype('int16') - img_height)
            self.ax.plot(x_points, y_points, linestyle="-")
    
    def show_plot(self):
        plt.show()
        plt.close() 

    @print_function_dec
    def plot_final_overlay(self, on_top='A', save_plot_as_img=False):        
        if(self.annotation_helper_obj and on_top != 'A'):
            self._plot_annotations(img_height)

        self._plot_the_fibers(img_height)

        if(self.annotation_helper_obj and on_top == 'A'):
            self._plot_annotations(img_height)
        
        if(save_plot_as_img):
            self.ax.set_frame_on(False)
            self.ax.axes.get_xaxis().set_visible(False)
            self.ax.axes.get_yaxis().set_visible(False)
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
            plt.margins(0,0)
            plt.tight_layout()
            plt.savefig('titties.tif', bbox_inches='tight',  pad_inches = 0, dpi=300)

    @print_function_dec
    def reset(self, new_tif=None):
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        if new_tif is not None:
            self.tif_file = new_tif
            self.set_img(new_tif)

@print_function_dec
def bucket_the_fibers(ctf_helper_obj,  annotation_helper_obj, buckets=np.array([0, 50, 150])):
    """Buckets Each fiber into an annotation for every annotation"""
    # Return Arr (len fibers, len anno) - For each fibers, we have an array for each annotation with represented bucket.
    fibers = ctf_helper_obj.get_fiber_verticies()
    centroids = ctf_helper_obj.get_centroids()

    shape = (len(fibers), len(annotation_helper_obj.geo_polygons))
    fibers_bucketed = np.ones(shape, dtype=int)
    for i, centroid in enumerate(centroids):
        centroid_x = centroid[0]
        centroid_y = centroid[1]
        centroid_point = geo.Point(centroid_x, centroid_y)
        fiber_linestring = geo.LineString(fibers[i])

        poly_distances = np.array(range(len(annotation_helper_obj.geo_polygons)))
        for j, g_poly in enumerate(annotation_helper_obj.geo_polygons):
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
    widths = ctf_output_obj.get_fiber_widths()
    
    labeled_fibers = bucketed_fibers.min(axis=1)
    print("SHAPES:", labeled_fibers.shape, lengths.shape, widths.shape)
    final_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    actual_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for i in range(len(bucketed_fibers)):
        final_counts[labeled_fibers[i]] +=  lengths[i] * widths[i]
        actual_counts[labeled_fibers[i]] +=1
    
    final_densities = []
    final_union_of_zones = annotation_helper_obj.get_final_zones([0, 50, 150]) 
    for i, zone in enumerate(reversed(final_union_of_zones)):
        final_densities.append(final_counts[i] / zone.area)

    print(actual_counts)
    return final_densities

if __name__ == '__main__':
    ctf_output = CTFIREOutputHelper(MAT_FILEPATH)

    annotation_helper = AnnotationHelper()
    anno_info, points, g_polygons = annotation_helper.get_annotations(EXPORTED_ANNOTATION_FILEPATH)

    # with open('bucketed.npy', 'rb') as f:
    #     bucketed_fibers = np.load(f)
    bucketed_fibers = bucket_the_fibers(ctf_output, annotation_helper)

    print(get_signal_density_overall(ctf_output, bucketed_fibers))


# print(get_signal_density_overall(ctf_output, bucketed_fibers))

# final_union_of_zones = annotation_helper.get_final_zones([0, 50, 150])
# [0.16245275053715674, 0.22054797976935003, 0.36467417044606637, 0.14896299113178588]

# epith_zone = annotation_helper.zoned_polys[26][1]
# medium_zone = annotation_helper.zoned_polys[26][2]
# # plot_fibers_per_zone(TIF_FILEPATH, ctf_output, bucketed_fibers)


# lengths = ctf_output.get_fiber_lengths()
# widths = ctf_output.get_fiber_widths()

# total, stromal, anno, stromal_percentage, annotation_percentage = get_annotation_areas(annotation_helper)
# poly = annotation_helper.geo_polygons[26]
# buckets_for_26th_anno = fiber_per_annotation = bucketed_fibers[:, 26:].flatten()
# final_counts = {0:0, 1:0, 2:0, 3:0}
# final_counts2 = {0:0, 1:0, 2:0, 3:0}


# for i, bucket in enumerate(buckets_for_26th_anno):
#     final_counts[bucket] += widths[i] * lengths[i]
#     final_counts2[bucket] +=1

# print(final_counts)
# print(final_counts2)
# cprint(f"Non-Stromal Area: {poly.area}", 'cyan')
# cprint(f"Eptih Area: {epith_zone.area}", 'green')
# cprint(f"Mid Area: {medium_zone.area}", 'cyan')
# cprint(f"Stromal Area: {stromal}", 'green')

# print("Non-Stromal:", final_counts[0] / poly.area)
# print("Epithelial:", final_counts[1] / epith_zone.area )
# print("Mid:", final_counts[2] / medium_zone.area)
# print("Stromal:", final_counts[3] / stromal)



# @print_function_dec
# def plot_fibers_per_zone(tif_filepath, ctf_output_obj, bucketed_fibers, annotation_helper_obj=None, on_top='A', bucket = 0, ax = None):
#     verts = ctf_output_obj.get_fiber_verticies()
#     img = plt.imread(tif_filepath)
#     img_width = img.shape[0]
#     img_height = img.shape[1]

#     if ax is None:
#         fig, ax = plt.subplots()
    
#     im = ax.imshow(img, cmap='gray', extent=[0, img_width+10, 0, img_height+10])

#     if(annotation_helper_obj and on_top != 'A'):
#         _plot_annotations(ax, annotation_helper_obj, img_height)
        
#     labeled_fibers = bucketed_fibers.min(axis=1)
#     indexes_to_plot = np.where(labeled_fibers == bucket)[0]
#     for i in indexes_to_plot:
#         x_points = verts[i][:, 0]
#         y_points = np.abs(verts[i][:, 1].astype('int16') - img_height)
#         ax.plot(x_points, y_points, linestyle="-", linewidth=x * 72 / fig.dpi)

#     _plot_zones(ax, annotation_helper, [0, 50, 150])

#     if(annotation_helper_obj and on_top == 'A'):
#         _plot_annotations(ax, annotation_helper_obj, img_height)

#     plt.show()
#     plt.close()






# dilated_poly = fixed_y_annotation_poly.buffer(150, single_sided=True)
# difference_poly = dilated_poly.difference(fixed_y_annotation_poly)        
# if(full_union_poly):
#     full_union_poly = full_union_poly.union(difference_poly)
# else:
#     full_union_poly = difference_poly

# plot_polygon(full_union_poly, ax, add_points = False, fill=True, linewidth = 2, alpha=1, 
#                 color=rgb_to_hex(tuple(annotation_helper_obj.annotation_info[i]['color'])))

# get_signal_density_per_annotation(annotation_helper, bucketed_fibers)

# total, stromal, anno, stromal_percentage, annotation_percentage = get_annotation_areas(annotation_helper)
# poly = annotation_helper.geo_polygons[26]

# buckets_for_26th_anno = fiber_per_annotation = bucketed_fibers[:, 26:].flatten()
# final_counts = {0:0, 1:0, 2:0, 3:0}
# final_counts2 = {0:0, 1:0, 2:0, 3:0}
# epith_zone = poly.buffer(50, single_sided=True)
# medium_zone = poly.buffer(150, single_sided=True)
# print(buckets_for_26th_anno.shape)
# for i, bucket in enumerate(buckets_for_26th_anno):
#     final_counts[bucket] += widths[i] * lengths[i]
#     final_counts2[bucket] +=1
# print(final_counts)
# print(final_counts2)
# cprint(f"Non-Stromal Area: {poly.area}", 'cyan')
# cprint(f"Eptih Area: {epith_zone.area - poly.area}", 'green')
# cprint(f"Mid Area: {medium_zone.area - epith_zone.area}", 'cyan')
# cprint(f"Stromal Area: {stromal}", 'green')

# print("Non-Stromal:", final_counts[0] / poly.area)
# print("Epithelial:", final_counts[1] / (epith_zone.area - poly.area))
# print("Mid:", final_counts[2] / (medium_zone.area - epith_zone.area))
# print("Stromal:", final_counts[3] / stromal)


# Non-Stromal: 0.07673755547855785
# Epithelial: 0.11958950881538306
# Mid: 0.1298023739063529
# Stromal: 0.198464111755657













#    poly2 = annotation_helper_obj.geo_polygons[20]
#     x2, y2 = poly2.exterior.xy
#     y_points2 = np.abs(np.array(y2) - img_height)
#     stacked2 = np.column_stack((x2, y_points2))
#     new_poly2 = geo.Polygon(stacked2)
#     new_x2, new_y2 =  new_poly2.exterior.xy
#     dilated_poly2 = new_poly2.buffer(150, single_sided=True)
#     difference_poly2 = dilated_poly2.difference(new_poly2)
#     dilated_x2, dilated_y2 = dilated_poly2.exterior.xy
    
#     diff_x2, diff_y2 = difference_poly2.exterior.xy

#     union_poly = difference_poly2.union(difference_poly)
    

    # ax.plot(*difference_poly.interiors[0].xy, color='orange') # Plot Dilated Annotation
    # ax.fill(new_x2, new_y2, color=rgb_to_hex(tuple(annotation_helper_obj.annotation_info[i]['color']))) # Plot OG Annotation
    
    # ax.fill(dilated_x2,  dilated_y2, color='green', alpha=.3) # Plot Dilated Annotation
    
    # ax.plot(*union_poly.exterior.xy, color='yellow') # Plot Dilated Annotation
    # ax.plot(diff_x2,  diff_y2, color='blue') # Plot Dilated Annotation

    # cprint(f"Area of Original: {new_poly2.area}", 'magenta')
    # cprint(f"Area of Dilated: {dilated_poly2.area}", 'green')
    # cprint(f"Area of Diff: {difference_poly2.area}", 'blue')
    # cprint(f"Area of Dilated - Original: {dilated_poly2.area - new_poly2.area}", 'yellow')

    # cprint(f"Area of UNION - Original: {union_poly.area}", 'cyan')
    # cprint(f"Area of SUM of Diffs - Original: {difference_poly2.area + difference_poly.area}", 'cyan')
    # cprint(f"Area of Sum of diff minus union - Original: {difference_poly2.area + difference_poly.area - union_poly.area}", 'white')

    # final_poly = dilated_poly2.intersection(dilated_poly)
    # final_poly2 = difference_poly2.intersection(difference_poly)
    # cprint(f"Area of FINAL DIL - Original: {final_poly.area}", 'white')
    # cprint(f"Area of FINAL DIFF - Original: {final_poly2.area}", 'white')
    # ax.fill(*final_poly.exterior.xy, color='orange') # Plot Dilated Annotation
    # ax.fill(*final_poly2.exterior.xy, color='purple') # Plot Dilated Annotation

    # diff_y_points = np.abs(np.array(diff_y) - img_height)
    # new_poly = aff.scale(poly, yfact = -1)
    # cprint(f"Area of Original: {final_poly.exter}", 'white')
    # ax.plot(*difference_poly.interiors.exterior.xy, 'orange') # Plot Dilated Annotation
    # ax.plot(intersected_x,  intersected_y, color='blue') # Plot Dilated Annotation


# cross product is tangent?
            # dilated_poly = new_poly.buffer(150, single_sided=True)
            # dilated_x, dilated_y = dilated_poly.exterior.xy
            # ax.plot(dilated_x,  dilated_y, color='green') # Plot Dilated Annotation

    # for i, points in enumerate(annotation_helper_obj.points):
    #     flat_points = points.astype(np.float32).flatten()
    #     # draw_img.line(flat_points, width=50,
    #     #               fill=tuple(annotation_helper_obj.annotation_info[i]['color']), joint="curve")

# print(calculate_signal_density_per_region(bucketed_fibers, verts, ls, np.mean(ws)))
# temp_img = convert_grayscale_tif_to_color(TIF_FILEPATH)

# # get_total_annotation_area(annotation_helper)
# calculate_signal_density_per_region(bucketed_fibers, verts)


# b_fibs = bucket_the_fibers(cents, verts, annotation_helper)
# unique, counts = np.unique(b_fibs[:, 26], return_counts=True)
# print(counts)
# print(unique)
# print(dict(zip(unique, counts)))
# b_fibs = bucket_the_fibers(np.array([[3410, 1585], [3400, 1820]]), verts, annotation_helper)
# print(type(b_fibs), b_fibs)

# verts = [np.array([[1200, 1800], [1201, 1800], [1202, 1800]]), np.array([[0, 0], [1, 2]]), np.array([[1205, 1800]])]
# print(calculate_signal_density_per_annotation(verts, annotation_helper))

# verts = ctf_output.get_all_fiber_vertices(TIF_FILEPATH)
# cents = ctf_output.get_centroids()
# dists, inds = get_closest_annotation(cents, annotation_helper)
# print(dists.shape, inds.shape)
#
# intersects, contains = check_if_fiber_in_annotated_region(verts, inds, cents, annotation_helper)
# print(intersects.shape, contains.shape)

# print(np.count_nonzero(intersects == 1))
# print(np.count_nonzero(contains == 1))
# print(len(verts))

# save_final_overlay(TIF_FILEPATH, annotation_helper)
# plot_final_overlay(TIF_FILEPATH, annotation_helper)

# print(g_polygons['DCIS']['polys'][-1].contains(geo.Point(1300, 1800)))
# print(g_polygons['DCIS']['polys'][-1].contains(geo.Point(2600, 1700)))

# fibs = [
#     np.array([[100,100], [200, 200], [300, 300], [130, 350],  [130, 300], [130, 300]]),
#     np.array([[150,150], [250, 250], [350, 350]]),
# ]
# print(calculate_signal_density_for_roi(fibs, 125, 325, 125, 325))

# # plot_final_overlay(TIF_FILEPATH, g_polygons)
#
# verts = ctf_output.get_fiber_verticies(TIF_FILEPATH)
# # verts = ctf_output.get_all_fiber_vertices(TIF_FILEPATH)
# cents = ctf_output.get_centroids()
# dists, inds = get_closest_annotation(cents[0:5], annotation_helper)
# print(dists, cents)
#
# intersects, contains = check_if_fiber_in_annotated_region(verts, inds, cents, polygons)
# print(np.count_nonzero(intersects == 1))
# print(np.count_nonzero(contains == 1))
# print(len(verts))
# [937.46306594 907.65742436 896.1880383  891.54977427 868.99079397] [[   3   87]
#  [  20  125]
#  [   1  223]
#  ...
#  [ 451 2084]
#  [3072  163]
#  [ 391 2338]]



# All Fibers: [0.0020944897030377224, 0.00646880335398254, 0.002293783019548474, 0.0047411148845995675, 0.00681346209823922, 0.010131100803597306, 0.0030365875977555494, 0.0011966717131544678, 0.0038102489706021174, 0.002241174232814847, 0.001217449318454479, 0.005356426785778678, 0.009523746536067882, 0.007889618600339397, 0.004388667480986708, 0.00296765994663061, 0.008691661731992505, 0.002626962168496938, 0.0037418143359002915, 0.005283722271593517, 0.004948988260398027, 0.005447451072416806, 0.0038796596468238733, 0.008922926067321075, 0.0035509250394453523, 0.003642882781227047, 0.004318426845005573]
# Thresholded Fibers: [0.0013090560643985764, 0.004635975737020821, 0.0019084274722643304, 0.0026959280716350484, 0.005982552086258827, 0.0072653312535757575, 0.0019696784417873835, 0.0007743169908646557, 0.003219003440681099, 0.0019040064278781001, 0.00043480332801945675, 0.002975792658765932, 0.007407358416941687, 0.0067625302288623415, 0.00308211762023494, 0.0020063053160319618, 0.005000495647250307, 0.001773926482785755, 0.0027523922759266567, 0.004579225968714381, 0.0026994481420352873, 0.0034440827805736285, 0.002742518026203083, 0.004989162962373075, 0.0020529752552284285, 0.002458511511336855, 0.0027759332622705633]

# TOP MOST: 2003 (1034.909090909091, 197.63636363636363)
# BOTTOM MOST: 2002 (1047.45, 2992.55)

# print(check_if_fiber_in_annotated_region(fibers, distances, final_centroids, polygons))


# plt.figure()
# plt.imshow(colored_img) 
# plt.show()  # display it



# def calculate_singal_density_of_all_stroma(bucketed_fibers, fibers, img_dimensions=[3700, 3700]):
#     indexes_where_value_in_annotations = np.where(np.any(bucketed_fibers == [0], axis=1))
#     mask = np.ones(bucketed_fibers.shape[0], dtype=bool)
#     mask[indexes_where_value_in_annotations] = False
#     # sub_geo_poly_array_per_centroid = bucketed_fibers[mask]
#     # all_stromal_fibers = fibers[indexes_of_fibers_in_stroma] IF I CAN MAKE FIBERS NP ARRAY

#     indexes_of_fibers_in_stroma = np.where(mask)
#     total_fiber_signal = 0
#     for i in indexes_of_fibers_in_stroma[0]:
#         total_fiber_signal += len(fibers[i])
#     total_area = img_dimensions[0] * img_dimensions[1]
#     return total_fiber_signal / total_area




# @print_function_dec
# def get_closest_annotation(centroids, annotations):
#     min_dist_values = []
#     min_dist_points_arr = []
#     for centroid in centroids[0:1]:
#         centroid_x = centroid[0]
#         centroid_y = centroid[1]
#         for i, annotation in enumerate(annotations):
#             min_dist = 99999999
#             min_dist_index = -1
#             min_dist_points = [1, 3]
#             for points in annotation['coords']:

#                 points_x = points[0]
#                 points_y = points[1]
#                 dist = math.sqrt( (centroid_x - points_x)**2 + (centroid_y - points_y)**2 )
#                 if(dist < min_dist):
#                     min_dist = dist
#                     min_dist_points = points
#                     min_dist_index = i
#         min_dist_points_arr.append({'centroid': centroid, 'annotated': min_dist_points, 'index': min_dist_index})
#         min_dist_values.append(min_dist)
#     # print(f"FINAL VALUES: {min_dist_values}")
#     # print(f"FINAL VALUES: {min_dist_points_arr}")
#     return min_dist_values, min_dist_points_arr

# cprint(get_closest_annotation(final_centroids, annotations), 'green')


# @print_function_dec
# def overlay_image_with_ctfire(image, mat_filepath, final_path_to_save='dong_overlayed.tif'):
#     # dict_keys(['__header__', '__version__', '__globals__', 'imgPath', 'imgName', 'savePath', 'cP', 'ctfP', 'p2', 'Iname', 'data'])
#     ctfire_export_dict = loadmat(mat_filepath) # Dict
#     ctfire_parameters = ctfire_export_dict['cP']
#     length_threshold = ctfire_parameters['LL1'][0][0][0][0]
#     ctfire_data = ctfire_export_dict['data']
#     ctfire_M_data = ctfire_data['M']

#     length_of_fibers = ctfire_M_data[0][0][0][0][1].flatten()
#     indexes_of_lengths_greater_than_threshold = np.where(length_of_fibers > length_threshold)
#     lengths_greater_than_threshold = np.where(length_of_fibers > length_threshold, length_of_fibers, 0)
#     lengths_greater_than_threshold = lengths_greater_than_threshold[lengths_greater_than_threshold != 0]

#     assert len(indexes_of_lengths_greater_than_threshold) == len(indexes_of_lengths_greater_than_threshold)

#     draw = ImageDraw.Draw(image)
    
#     img_width = image.width
#     img_height = image.height

#     all_centroids = np.zeros((len(length_of_fibers), 2), dtype='int16')
    
#     for i in range(len(length_of_fibers)):
#     # for i in range(5):
#         vertices_to_use = ctfire_data['Fa'][0][0][0][i]['v'][0]
#         xa_data = ctfire_data['Xa'][0][0]
#         xy_points = xa_data[vertices_to_use-1]
#         x_points = xy_points[:, 0].astype('int16')
#         y_points = np.absolute(xy_points[:, 1].astype('int16') - img_height)
#         y_points = xy_points[:, 1].astype('int16')
#         centroid = centeroidnp(x_points, y_points)
#         all_centroids[i] = centroid
#         coords = np.stack((x_points, y_points), axis=1)
#         draw.line(coords.flatten().astype(np.float32), width=10, fill=tuple(np.random.choice(range(256), size=3)), joint="curve")
    #     draw = ImageDraw.Draw(image)
#     final_path = os.path.join(sys.path[0], final_path_to_save)
#     image.save(final_path)
#     final_path = os.path.join(sys.path[0], final_path_to_save)
#     image.save(final_path)

#     return all_centroids, image


# exported_annotation_file_path = os.path.join(sys.path[0], "./ANNOTATED-DCIS-018_10x10_1_Nuclei_Collagen - Denoised.geojson")


# temp_tif = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\CT-FIRE output\DCIS-128_4\ctFIREout\OL_ctFIRE_DCIS-128_10x10_4_Nuclei_Collagen-0001.tif"
# annotations, polygons, g_polygons = get_annotations(exported_annotation_file_path)
# final_tif_path = add_annotations(convert_grayscale_tif_to_color(temp_tif) , annotations, 'dong4.tif')

# tif_filepath = os.path.join(sys.path[0], "../Denoised_images/DCIS-018_10x10_1_Nuclei_Collagen - Denoised.tif")
# colored_img = convert_grayscale_tif_to_color(tif_filepath)
# # final_tif_path = add_annotations(colored_img, annotations)
# mat_filepath = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\ctFIREout_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

# cens, img = overlay_image_with_ctfire(colored_img, mat_filepath)
# final_tif_path = add_annotations(img , annotations, 'dong3.tif')
# def convert_grayscale_tif_to_color(image_url):
#     image = Image.open(image_url, 'r')
#
# #     return rgbimg
#
# def _plot_image_annotations_fibers(tif_path, verticies, geo_polygons, on_top='A'):
#     img = plt.imread(tif_path)
#     img_width = img.shape[0]
#     img_height = img.shape[1]
#
#     fig, ax = plt.subplots()
#     im = ax.imshow(img, cmap='gray', extent=[0, img_width + 10, 0, img_height + 10])
#
#     if(on_top != 'A'):
#         _plot_annotations(ax, geo_polygons, img_height)
#
#     for i in range(len(verticies)):
#         x_points = verticies[i][:, 0]
#         y_points = verticies[i][:, 1]
#         y_points = np.absolute(verticies[i][:, 1].astype('int16') - img_height) # Need to do this for plotting as (0,0) is bottom left
#
#         ax.plot(x_points, y_points, linestyle="-")
#
#     if(on_top == 'A'):
#         _plot_annotations(ax, geo_polygons, img_height)
#
#     plt.show()
#     plt.close()


# final_centroids = []
# with open('centroids.npy', 'rb') as f:
#      final_centroids = np.load(f)
# print(final_centroids.shape)

# fibers = []
# with open('all_coords_16.json', 'r') as f:
#     fibers = json.load(f)
# print(len(fibers))
# @print_function_dec
# def add_annotations(image_url, annotations, filepath_to_save="dong2.tif"):
#     new_colored_img = convert_grayscale_tif_to_color(image_url)
#     draw = ImageDraw.Draw(new_colored_img)
#     for annotation_obj in annotations
#         annotation_points = annotation_obj['points']
#         annotation_color = annotation_obj['color']
#         draw.line(annotation_points.astype(np.float32), width=70, fill=tuple(annotation_color), joint="curve")
#     final_path = os.path.join(sys.path[0], filepath_to_save)
#     new_colored_img.save(final_path)
#     return final_path

# print(dists[0])
# print(inds[0])
# print(dists[2001])
# print(dists[2002])
# print(dists[2003])
# for i in range(2001, 2004):
#     vert_to_check =  verts[i]
#     vert_path = patches.Path(vert_to_check)
#     print(len(polygons))
#     print(vert_path.intersects_path(polygons[0].get_path(), filled=False))
#     print(polygons[0].contains_points([cents[i]]))
#     print()

        # if(intersection_array[i] and contains_array[i]):
        #     cprint(f"{i}, {centroid}, {distances[i]}", 'cyan')
        #
        # if(intersection_array[i] and not contains_array[i]):
        #     cprint(f"{i}, {centroid}, {distances[i]}", 'green')
        #
        # if(not intersection_array[i] and contains_array[i]):
        #     cprint(f"{i}, {centroid}, {distances[i]}", 'yellow')
    #
    # x, y = new_poly.exterior.xy
    # for j in range(1):
    #     temp_x = x[j]
    #     temp_y = y[j]
    #
    #     line_string = geo.LineString([(temp_x, temp_y), (cent.x, cent.y)])
    #     new_scale = 150 / line_string.length
    #
    #     new_line_string = aff.scale(line_string, 1 + new_scale, 1 + new_scale)
    #     new_bounds = new_line_string.bounds
    #
    #     if (new_bounds[2] > cent.x):  # If MaxX (end part of new_line)
    #         new_bounds_x = new_bounds[2]
    #     else:
    #         new_bounds_x = new_bounds[0]
    #
    #     if (new_bounds[3] > cent.y):  # IfMaxY is greater than cent
    #         new_bounds_y = new_bounds[3]
    #     else:
    #         new_bounds_y = new_bounds[1]
    #
    #     diff_x, diff_y = (cent.x - new_bounds_x, cent.y - new_bounds_y)
    #     print(diff_x, diff_y)
    #     new_line_string = aff.translate(new_line_string, diff_x, diff_y)  # 150 more
    #     if (diff_x > 0):
    #         final_x = new_line_string.bounds[0]
    #     else:
    #         final_x = new_line_string.bounds[2]
    #
    #     if (diff_y > 0):
    #         final_y = new_line_string.bounds[1]
    #     else:
    #         final_y = new_line_string.bounds[3]
    #
    #     new_poly_coords[j] = np.array([[final_x, final_y]])
    #     ax.plot(line_string.coords.xy[0], line_string.coords.xy[1], color='green')
    #     ax.plot(new_line_string.coords.xy[0], new_line_string.coords.xy[1], color='orange')  #
    #
    #     # final_scale = new_line_string.length / line_string.length
    #     # final_offest = final_scale - 1
    #
    # # new_poly = aff.affine_transform(new_poly, [final_scale, 0, 0, final_scale, final_offest * -cent.x, final_offest * -cent.y]) # Subtract 100 percent.
    # # new_x, new_y = new_poly.exterior.xy
    #
    # ax.plot(x, y, color=rgb_to_hex(tuple(annotation_helper_obj.annotation_info[i]['color'])))  # Plot OG Annotation
    # # ax.plot(new_x, new_y, color='green') # Plot Scaled bro
    #
    # print(new_poly_coords.shape)
    # print(new_poly_coords[0])
    # ax.plot(new_poly_coords[:, 0], new_poly_coords[:, 1], color='blue')
    #
    # # ax.plot(new_line_string.coords.xy[0], new_line_string.coords.xy[1], color='blue') #
    # # ax.plot(line_string.coords.xy[0], line_string.coords.xy[1], color='red')