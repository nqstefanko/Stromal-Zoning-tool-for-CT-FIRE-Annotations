from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from numpyencoder import NumpyEncoder
from termcolor import cprint, colored

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import shapely.geometry as geo # Polygon, Point

from ctfire_output_helper import CTFIREOutputHelper
from annotation_helper import AnnotationHelper
from test_export import *

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

annotation_helper = AnnotationHelper()
ctf_output = CTFIREOutputHelper(MAT_FILEPATH)
draw_helper = DrawingHelper(ctf_output, annotation_helper, TIF_FILEPATH)
anno_info, points, g_polygons = annotation_helper.get_annotations(EXPORTED_ANNOTATION_FILEPATH)


# {0: 1262, 1: 1064, 2: 1358, 3: 2935}

############################## NEW TEST - Save Overlay Annotations on Top #######################################################################################
# draw_helper.save_final_overlay()
############################################################################################################################################
# bucketed_fibers = bucket_the_fibers(ctf_output, annotation_helper, 'bucketed.npy', False)
bucketed_fibers = bucket_the_fibers(ctf_output, annotation_helper)
print(bucketed_fibers.shape)
labeled_fibers = bucketed_fibers.min(axis=1)
unique, counts = np.unique(labeled_fibers, return_counts=True)
print(dict(zip(unique, counts)))
print(bucketed_fibers.shape)
print(get_signal_density_overall(ctf_output, annotation_helper, bucketed_fibers))


np.save('bucketed.npy', bucketed_fibers.astype(np.int32))
# with open('bucketed.npy', 'rb') as f:
#      bucketed_fibers = np.load(f)
for i in range(4):
    draw_helper.reset(TIF_FILEPATH)
    draw_helper.draw_fibers_per_zone(bucketed_fibers, i)
    final_path = os.path.join(sys.path[0], 'bong_overlayed.tif')
    draw_helper.rgbimg.save(final_path)
    plot_helper = PlottingHelper(ctf_output, annotation_helper, final_path)
    plot_helper._plot_zones([0, 50, 150], to_plot=[3-i])
    plot_helper.show_plot()
    
    #1 is mid, 2 is epith, 3 is interior

############################## NEW TEST - Save Overlay Annotations on Bottom #######################################################################################
# save_final_overlay(TIF_FILEPATH, annotation_helper, on_top='F')
############################################################################################################################################

############################## NEW TEST - Save Overlay No Annotations#######################################################################################
# save_final_overlay(TIF_FILEPATH)
############################################################################################################################################

############################# NEW TEST - Plot Overlay Annotations on Top ######################################################################################################
# plot_helper.plot_final_overlay()
# plot_helper.show_plot()
###########################################################################################################################################

############################## NEW TEST - Plot Overlay Annotations on Bottom ######################################################################################################
# plot_final_overlay(TIF_FILEPATH, annotation_helper, on_top='F')
###########################################################################################################################################

############################## NEW TEST - Plot Overlay no Annotations ######################################################################################################
# plot_final_overlay(TIF_FILEPATH)
############################################################################################################################################

############################## NEW TEST - Plot stromal Zones ######################################################################################################
# for i in range(1):
#     plot_fibers_per_zone(TIF_FILEPATH, ctf_output, bucketed_fibers, bucket=i)
# ASK HOW TO CATEGORIZE FIBERS WITHIN ANNOTATIONS / CANCERES/ ATYPIA / BENIGN
# Are the any that include ones that overlap, 
############################################################################################################################################

############################## NEW TEST - Get Average Width Per Stromal Zone ######################################################################################################
# cprint(f"Average Widths per Zone: {get_average_width_per_zone(ctf_output, bucketed_fibers)}", 'cyan')
############################################################################################################################################

############################## NEW TEST - Get Average Width Per Stromal Zone ######################################################################################################
# cprint(f"Average Lengths per Zone: {average_length_per_zone(ctf_output, bucketed_fibers)}", 'cyan')
############################################################################################################################################

############################## NEW TEST - Get Signal Density Per Stromal Zone AAASSSSSSKKKKK ######################################################################################################
# cprint(f"Signal Density per Zone: {calculate_signal_density_per_zone(ctf_output, bucketed_fibers)}", 'cyan')
# Ask What consists of signal density, length * width or count of pixels
# Just based off of  pixel count, and SHG images?
# Threshold, pixels vlaues, adnything belwo that is black and evreything is white. 
# Oupput: Zone Regions, and density is based
#Meth based all on CT-Fire output 
# 1 make it based on length and width
# Make it based on area of zones
# Dilate image based on pixels? Then get area?
############################################################################################################################################

############################## NEW TEST - Get Annotation Areas ea ######################################################################################################
# total_area, stromal_area, annotation_area, stromal_percentage, annotation_percentage = get_annotation_areas(annotation_helper)
# cprint(f"Total Area: {total_area}", 'cyan')
# cprint(f"Stromal Area: {stromal_area}", 'cyan')
# cprint(f"Annotation Area: {annotation_area}", 'cyan')
# cprint(f"Stromal percentage: {stromal_percentage}", 'cyan')
# cprint(f"Annotation percentage: {annotation_percentage}", 'cyan')
# cprint(f"Sum Areas: {stromal_area + annotation_area}", 'cyan')
# cprint(f"Sum percentage: {stromal_percentage + annotation_percentage}", 'cyan')
############################################################################################################################################

############################## NEW TEST - Get Signal Density Per Annotation AAASSSSSSKKKKK ######################################################################################################
# cprint(f"Signal Density per Annotation: {calculate_signal_density_per_annotation(ctf_output, annotation_helper)}", 'cyan')
# # NOTE: BASED ON PIXELS OF FIBERS NOT LENTH * WIDTH RNNNN
############################################################################################################################################


# ############################## NEW TEST - Try adding annotations with already overlay ######################################################################################################
# little_tif = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\CT-FIRE output\DCIS-002_1\ctFIREout\OL_ctFIRE_DCIS-002_10x10_1_Nuclei_Collagen-0001.tif"
# rgbimg = convert_grayscale_tif_to_color(little_tif)
# draw = ImageDraw.Draw(rgbimg)
# _draw_annotations(annotation_helper, draw, "bong1.tif")
# ############################################################################################################################################


# TODO: 
# 1. Optimize as much as possible (Convert as much to np as possible)
# 2. Be able to save, pickle info?
# 3. Work on Linearity
# 4. Normalize Plotting of Annotations, Fibers so widths are correct and adjustable
# 5. Improve Code to be more linear
# 6. Make code user friendly :0
# 7. Relationship btwn fibers? More fibers that are linear?
# PEr annotation type analyss like len, widht
# And hwo straigt they area.

# Use further tools to assess collagen uniformity, and fiber-fiber alignment and fiber-epithelial edge alignment. If possible.
# Across multiple, DCIS Ducsts, wanted to see hotspts (small regions (each annotaiton by pathologist a singel duct) that are more dense)
# Larer DCIS v smaller DCIS duct
# OUTPUT: Another plot is saved and associated with file, repsented plots that shows this data gets this plot, and you cna 

# Verbose Guide on how to run and plot associated files. 


# verts = ctf_output.get_fiber_verticies()
# cents = ctf_output.get_centroids()
# print(get_average_width_per_zone(ctf_output, bucketed_fibers))
# print(average_length_per_zone(ctf_output, bucketed_fibers))
#  plot_specific_zone(TIF_FILEPATH, ctf_output, bucketed_fibers, annotation_helper)

# temp_img = convert_grayscale_tif_to_color(r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\OL_ctFIRE_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.tif")
# anno_info, points, g_polygons = annotation_helper.get_annotations(EXPORTED_ANNOTATION_FILEPATH)
# verts = ctf_output.get_fiber_verticies(TIF_FILEPATH)
# cents = ctf_output.get_centroids()
# b_fibs = bucket_the_fibers(cents, verts, annotation_helper)
# unique, counts = np.unique(b_fibs[:, 26], return_counts=True)
# print(counts)
# print(unique)
# print(dict(zip(unique, counts)))





# TO SAVE:

# C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\dcis_code\ctfire_output_helper.py 459