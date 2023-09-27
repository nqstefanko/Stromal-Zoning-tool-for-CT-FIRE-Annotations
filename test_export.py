from PIL import Image, ImageDraw, ImageFont, ImageColor
from datetime import datetime
from numpyencoder import NumpyEncoder
from pprint import pprint
from scipy.io import loadmat
from termcolor import cprint, colored
import shapely
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import shapely.geometry as geo # Polygon, Point
from dcis_utils import print_function_dec

from ctfire_output_helper import CTFIREOutputHelper
from annotation_helper import AnnotationHelper
from shapely.plotting import plot_polygon
import multiprocessing as mp #import Pool

# https://stackoverflow.com/questions/57657419/how-to-draw-a-figure-in-specific-pixel-size-with-matplotlib

# #CROPPED_IMG DATA
# TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.tif"
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout\ctFIREout_2B_D9_crop2.mat"

#16 DENOISED DATA 16
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-016_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-016_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\ctFIREout\ctFIREout_DCIS-016_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

# #18 DENOISED DATA 18
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-018_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-018_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\ctFIREout_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

# with Image.open(TIF_FILEPATH) as img:
#     IMG_DIMS = img.size

def sort_by_area(lst):
    def get_area(elem):
        return elem[0].area
    return sorted(lst, key=get_area, reverse=True)

COLORS = ['white', 'magenta', 'orange', 'green', 'cyan', 'red', 'blue', 'pink', 'yellow', 'brown']
COLORS_HEX = [
    '#FFFFFF',  # White
    '#FF00FF',  # Magenta
    '#FFA500',  # Orange
    '#008000',  # Green
    '#00FFFF',  # Cyan
    '#FF0000',  # Pink
    '#0000FF',  # Blue
    '#FFC0CB',  # Pink
    '#FFFF00',  # Yellow
    '#713225'   # Brown
]

class DrawingHelper():
    def __init__(self, tif_file=None) -> None:
        self.tif_file = tif_file
        self.rgbimg =  self._convert_grayscale_tif_to_color()
        self.draw_image = ImageDraw.Draw(self.rgbimg)

    def _draw_polygon_helper(self, polygon, color, annos, all_polys):
        """There is more complication to the fact that the polygons themselves are not the same! They can either be a polygon with a 
        MultiString Boundary or a LineString Boundary (or a linearRing from the interior of a MultiString). So we need to tackle these separately"""
        if type(polygon.boundary) == shapely.geometry.MultiLineString:
            if len(polygon.boundary.geoms) > 0:
                all_polys.append([shapely.geometry.Polygon(polygon.exterior) ,color])
                
            # for interior in polygon.interiors:
            #     if(annos.contains(interior.centroid)):
            #         temp_color = COLORS[COLORS.index(color) - 1]
            #     else:
            #         temp_color = COLORS[COLORS.index(color) + 1]
            #     poly_bro = shapely.geometry.Polygon(interior)
            #     all_polys.append([poly_bro, color])
        elif type(polygon) == shapely.geometry.LinearRing:
            poly = shapely.geometry.Polygon(polygon)
            all_polys.append([poly ,color])            
        else:
            all_polys.append([shapely.geometry.Polygon(polygon.exterior), color])
            
    def _draw_helper(self, final_union_poly, color, annos, all_polys):
        """All of the polygons that are generated from our unioning/intersecting/differencing can either be a MutliPolygon or a Polygon,
        and we need to address these differently"""
        if type(final_union_poly) == shapely.geometry.MultiPolygon:
            for polygon in final_union_poly.geoms:
                self._draw_helper(polygon, color, annos, all_polys)
        elif type(final_union_poly) == shapely.geometry.Polygon:
            self._draw_polygon_helper(final_union_poly, color, annos, all_polys)
    
    def draw_zones(self, list_of_union_zones, delete_zones, to_draw=[], colors=COLORS, opacity=32):
        "This lad helps draw FILLED IN Zones."
        all_polys = []
        for i, final_union_zone_polygon in enumerate(list_of_union_zones):
            # 0 is Stromal, 1 is mid, 2 is epith, 3 is annotation itself
            if final_union_zone_polygon.area > 0:
                color = colors[i % len(colors)]
                self._draw_helper(final_union_zone_polygon, color, list_of_union_zones[0], all_polys)
        
        if(delete_zones and delete_zones.area > 10):
            color = 'clear'
            self._draw_helper(delete_zones, color, delete_zones, all_polys)
                    
        sorted_list = sort_by_area(all_polys)
        for poly_list in sorted_list:
            # print(poly_list[0].area, poly_list[1], COLORS.index(poly_list[1]) in to_draw)
            if(poly_list[1] != 'clear' and (COLORS.index(poly_list[1]) in to_draw or not to_draw)):
                self.draw_image.polygon(np.array(poly_list[0].exterior.coords).astype('float32'), width=4,
                                        fill=ImageColor.getrgb(poly_list[1]) + (opacity,), outline=ImageColor.getrgb(poly_list[1]) + (128,))
            else:
                self.draw_image.polygon(np.array(poly_list[0].exterior.coords).astype('float32'),
                                        fill=ImageColor.getrgb('red') + (0,), width=3, outline=ImageColor.getrgb('red') + (0,))
       
    def _draw_zone_outline_helper(self, polygon, colors, current_depth, to_draw):
        color = colors[current_depth]
        lining = ImageColor.getrgb(color) + (128,)
        width_size = int(self.image.size[0] / 100)
        if type(polygon.boundary) == shapely.geometry.MultiLineString:            
                self.draw_image.polygon(list(polygon.exterior.coords), width=width_size, outline=lining)
                for interior in polygon.interiors:
                    new_depth = current_depth + 1
                    if(new_depth in to_draw):
                        new_lining = ImageColor.getrgb(colors[current_depth - 1]) + (128,)
                        self.draw_image.polygon(list(interior.coords), width=width_size, outline=new_lining)
                    elif(current_depth in to_draw):
                        self.draw_image.polygon(list(interior.coords), width=width_size, outline=lining)
        else:
            coords = np.array(polygon.exterior.coords).astype('float32')
            self.draw_image.polygon(coords, width=width_size, outline=lining)

    def draw_zone_outlines(self, list_of_union_zones, to_draw=[],  colors = COLORS):
        to_draw = list(to_draw)
        for i in range(len(list_of_union_zones)):
            union_poly = list_of_union_zones[i]
            if((not to_draw or i in to_draw) and union_poly.area > 0):
                if(type(union_poly) == shapely.geometry.multipolygon.MultiPolygon):
                    for polygon in union_poly.geoms:
                        self._draw_zone_outline_helper(polygon, colors, i, to_draw)
                else:
                    self._draw_zone_outline_helper(union_poly, colors, i, to_draw)
    
    def _convert_grayscale_tif_to_color(self):
        self.image = Image.open(self.tif_file, 'r').convert('RGBA')
        rgbimg = Image.new("RGBA", self.image.size)
        rgbimg.paste(self.image)
        return rgbimg

    def draw_annotations(self, annos_to_draw, draw_anno_indexes=False):
        font = ImageFont.truetype("arial.ttf", int(self.image.size[0] / 36))
        for annotation in annos_to_draw:
            poly = annotation.geo_polygon
            x, y = poly.exterior.xy
            flat_points2 = np.stack((x, y), axis=1).flatten()
            self.draw_image.line(flat_points2.astype(np.float32), width=15, fill=tuple(annotation.color), joint='curve')

            if draw_anno_indexes:
                xcent = poly.centroid.coords.xy[0][0]
                ycent = poly.centroid.coords.xy[1][0]
                self.draw_image.text([xcent, ycent], f"{annotation.original_index}: {annotation.name}",
                                     font=font,
                                     fill=tuple(annotation.color))
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

    def draw_fibers_colored_per_zone(self, verts, widths, fiber_zones):
        for i in range(len(verts)):
            fill = ImageColor.getrgb(COLORS[fiber_zones[i]])
            self.draw_image.line(
                verts[i].flatten().astype(np.float32),
                width=int(round(widths[i])),
                fill=fill,
                joint="curve"
            )
        self.image = Image.alpha_composite(self.image, self.rgbimg)

    def draw_overlay(self, draw_functions):
        for draw_function in draw_functions:
            draw_function()

    def get_image(self):
        return Image.alpha_composite(self.image, self.rgbimg)

    def save_file_overlay(self, final_path_to_save='images/bong_overlayed.tif'):
        cprint(f"Saving Overlay to {final_path_to_save}...", 'cyan')
        final_path = os.path.join(sys.path[0], final_path_to_save)
        composite_image = Image.alpha_composite(self.image, self.rgbimg)
        composite_image.save(final_path)
        return final_path
 
    def draw_fibers_per_zone(self, verts, widths, bucketed_fibers, to_draw = [0, 1, 2, 3], colored_zone = False):
        for bucket in to_draw:
            indexes_to_plot = np.where(bucketed_fibers == bucket)[0]
            for i in indexes_to_plot:
                if(colored_zone):
                    color_fill = COLORS[bucket]
                else:
                    color_fill = tuple(np.random.choice(range(256), size=3))
                self.draw_image.line(verts[i].flatten().astype(np.float32), width=int(round(widths[i])), fill=color_fill, joint="curve")
        self.image = Image.alpha_composite(self.image, self.rgbimg)
     
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
                plot_polygon(final_union_zone_polygon, self.ax, add_points = False, fill=True, linewidth = 0, alpha=.55, color=colors[i])
        return list_of_union_zones

    def _plot_fibers(self, verts):
        for i in range(len(verts)):
            x_points = verts[i][:, 0]
            y_points = np.abs(verts[i][:, 1].astype('int16') - self.img_dims[1])
            self.ax.plot(x_points, y_points, linestyle="-")
    
    def _plot_fibers_per_zone(self, verts, bucketed_fibers, to_plot = [0, 1, 2, 3]):
        for bucket in to_plot:
            indexes_to_plot = np.where(bucketed_fibers == bucket)[0]
            for i in indexes_to_plot:
                x_points = verts[i][:, 0]
                y_points = np.abs(verts[i][:, 1].astype('int16') - self.img_dims[1])
                self.ax.plot(x_points, y_points, linestyle="-")

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
        self.annotations_indexes_distanced_on = None
        self.fiber_dists = None
        
        self.bucketed_fibers = None
        self.crunched_fibers = None
        self.current_fibers = None
        
        self.list_of_zones = None
        self.delete_zones = None
        
        self.combo_zones_numbers = {}
    
    @print_function_dec
    def get_all_fiber_dists_for_each_anno(self, fibers, centroids, annotations):
        fiber_dists = np.ones(
            (len(fibers), len(annotations)),
            dtype=int
        )
        
        for i, centroid in enumerate(centroids):
            centroid_x = centroid[0]
            centroid_y = centroid[1]
            centroid_point = geo.Point(centroid_x, centroid_y)
            fiber_linestring = geo.LineString(fibers[i])
            poly_distances = np.array(range(len(annotations)))
            for j, annotation in enumerate(annotations):
                g_poly = annotation.geo_polygon
                poly_distances[j] = g_poly.exterior.distance(centroid_point)
                
                if (g_poly.contains(centroid_point)):  # Could use fiber_linestring but much more restrictive  or g_poly.contains(fiber_linestring)
                    poly_distances[j] = -1

                if(fiber_linestring.crosses(g_poly)):
                    poly_distances[j] = 1
            
            fiber_dists[i] = poly_distances
        self.fiber_dists = fiber_dists 
        return fiber_dists

    def get_bucket_for_each_fiber(self, base_annos, buckets=np.array([0, 50, 150], dtype=int)):
        """Takes all distances for each fiber and anno, and gets a single bucket for each fiber that it falls into"""
        if self.fiber_dists is None:
            cprint("Fiber Distances Not Set. Cannot Bucket!", "red")
            return 
        return np.digitize(np.min(self.fiber_dists[:, base_annos], axis=1), buckets, right=True).astype(int)

    def reset(self):
        self.annotations_indexes_distanced_on = None
        self.fiber_dists = None
        
        self.bucketed_fibers = None
        self.crunched_fibers = None
        self.current_fibers = None
        
        self.list_of_zones = None
        self.delete_zones = None
        
        self.combo_zones_numbers = {}

@print_function_dec
def get_all_fiber_dists_for_each_anno(fibers, centroids, annotations):
    fiber_dists = np.ones(
        (len(fibers), len(annotations)),
        dtype=int
    )
    
    for i, centroid in enumerate(centroids):
        centroid_x = centroid[0]
        centroid_y = centroid[1]
        centroid_point = geo.Point(centroid_x, centroid_y)
        fiber_linestring = geo.LineString(fibers[i])
        poly_distances = np.array(range(len(annotations)))
        for j, annotation in enumerate(annotations):
            g_poly = annotation.geo_polygon
            poly_distances[j] = g_poly.exterior.distance(centroid_point)
            
            if (g_poly.contains(centroid_point)):  # Could use fiber_linestring but much more restrictive  or g_poly.contains(fiber_linestring)
                poly_distances[j] = -1

            if(fiber_linestring.crosses(g_poly)):
                poly_distances[j] = 1
        
        fiber_dists[i] = poly_distances
        
    return fiber_dists

def get_bucket_for_each_fiber(fiber_dists, buckets=np.array([0, 50, 150], dtype=int)):
    """Takes all distances for each fiber and anno, and gets a single bucket for each fiber that it falls into"""
    return np.digitize(np.min(fiber_dists, axis=1), buckets, right=True).astype(int)

def get_crunched_fibers(fiber_dists, anno_indexes, base_indexes, buckets=np.array([0, 50, 150]), to_ignore=[0,1]):
    all_bucketed_fibers = get_bucket_for_each_fiber(fiber_dists[:, base_indexes], buckets)
    all_bucketed_fibers_of_selected_values = get_bucket_for_each_fiber(fiber_dists[:, anno_indexes], buckets)
    final_crunched = _create_new_array(all_bucketed_fibers, all_bucketed_fibers_of_selected_values, len(buckets), to_ignore)
    return final_crunched
    
def _create_new_array(a, b, chosen_value, to_ignore):
    """
    Given two numpy arrays `a` and `b` of equal length, create a new array of
    equal length where if the value in `b` is less than or equal to the value in `a`,
    then set it to the value in `b`. Else set it to a value of `chosen_value`.
    """
    new_array = np.zeros_like(a, dtype=int)
    for i in range(len(a)):
        if b[i] <= a[i]:
            new_array[i] = b[i]
        else:
            if(a[i] in to_ignore):
                new_array[i] = chosen_value + 1
            else:
                new_array[i] = a[i]
            #     chosen_value
            # new_array[i] = chosen_value
    return new_array

def get_fiber_density_and_counts_per_zone(lengths, widths, fiber_dists_bucketed, buckets=np.array([0, 50, 150])):
    """Gets actual and sum counts of every fiber for every zone
        Inputs:
            lengths: 
            widths:
            fiber_dists: output from get_all_fiber_dists_for_each_anno
            buckets: zones
        Outputs 
            final_counts: sum of areas of fibers
            actual_counts: number of fibers
    NOTE: 
        # final_counts is equivalent to:
        # for i, bucket in enumerate(fiber_dists_bucketed):
        #     final_counts[bucket] += prods[i]
    """
    final_counts = np.zeros(len(buckets) + 1) # Ex: [0, 0, 0, 0]
    
    actual_counts = np.bincount(fiber_dists_bucketed, minlength=len(buckets) + 1).astype(int) # Represents number of fibers in each zone
    prods = lengths * widths 
    final_counts = np.bincount(fiber_dists_bucketed, weights=prods, minlength=len(buckets) + 1).astype(int) #represents sum of areas of fibers in each zone
    return final_counts, actual_counts

def get_signal_density_per_annotation(fiber_dists_indexed, annotation,  lengths, widths):
    fibs_inds_in_anno = np.where(fiber_dists_indexed == -1)
    length_of_fibs_in_anno = lengths[fibs_inds_in_anno]
    width_of_fibs_in_anno = widths[fibs_inds_in_anno]
    final_density = np.sum(length_of_fibs_in_anno * width_of_fibs_in_anno)
    return final_density / annotation.geo_polygon.area

def get_signal_density_for_all_annotations(fiber_dists, annotations, lengths, widths):
    all_signal_dens_per_annotations = np.zeros(len(annotations))
    for i, anno in enumerate(annotations):
        all_signal_dens_per_annotations[i] = get_signal_density_per_annotation(fiber_dists[:, i], anno, lengths, widths)
    return all_signal_dens_per_annotations

def get_signal_density_per_desired_zones(zone_sums, final_union_of_zones, zones):
    final_area = 0
    final_density = 0
    
    total_area = 0
    total_density = 0
    for i, zone in enumerate(final_union_of_zones):
        total_area += zone.area
        total_density += zone_sums[i]
        
        if(i in zones):
           final_area += zone.area
           final_density += zone_sums[i]
    
    return final_density / final_area

def get_measure_value_per_zone(values, bucketed_fibers, measurement, num_of_zones=4):
    """
    # This is used to calculate values (mean, median, etc) from measurements of length, width, and angle per zones
    Inputs: 
        values:  measuresments to calculate - Ex: lengths, widths, angles
        bucketed_fibers: Bucketed Fibers - Ex: output from get_bucket_for_each_fiber
        measurement: Function to get measurements - Ex: np.mean, np.median, np.std
        num_of_zones: Number of Zones - Ex: 4
    """
    final_counts = {}
    for i in range(num_of_zones):
        final_counts[i] = 0

    for i in range(num_of_zones):
        labeled_values = values[np.where(bucketed_fibers == i)]
        if(not labeled_values.any()):
            value_mean = 0
        else:
            value_mean = measurement(labeled_values)
        final_counts[i] = value_mean
    return final_counts

if __name__ == '__main__':
    pass


