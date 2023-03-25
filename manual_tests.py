from ctfire_output_helper import CTFIREOutputHelper
from annotation_helper import AnnotationHelper
from test_export import *
from termcolor import cprint, colored

# # CROPPED_IMG DATA CROP 2
# TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.tif"
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout_2B_D9_crop2.mat"
# EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.geojson"

# CROPPED_IMG DATA CROP 1
TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop1.tif"
MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout_2B_D9_crop1.mat"
EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop1.geojson"

#16 DENOISED DATA 16
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-016_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-016_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\ctFIREout\ctFIREout_DCIS-016_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

# #18 DENOISED DATA 18
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-018_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-018_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\ctFIREout_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

with Image.open(TIF_FILEPATH) as img:
    IMG_DIMS = img.size

CTF_OUTPUT = CTFIREOutputHelper(MAT_FILEPATH)
DRAW_HELPER = DrawingHelper(TIF_FILEPATH)
ANNOTATION_HELPER = AnnotationHelper(EXPORTED_ANNOTATION_FILEPATH, IMG_DIMS)
PLOT_HELPER = PlottingHelper(tif_file=TIF_FILEPATH)

# plt.ion()

def test_plot_annotations():
    PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations)
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    
    PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.get_specific_annotations())
    PLOT_HELPER.show_plot()

def test_plot_annotations_of_correct_name():
    PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.get_specific_annotations(['DCIS']))
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    
    ANNOTATION_HELPER.set_annotations(['Ignore'])
    PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations)
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    
    ANNOTATION_HELPER.reset_annotations()
    PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations)
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    
def test_plot_annotations_with_indexes():
    PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations, plot_anno_indexes=True)
    PLOT_HELPER.show_plot()

def test_plot_fibers():
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    PLOT_HELPER._plot_fibers(verts)
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    
    verts = CTF_OUTPUT.get_fiber_vertices()
    PLOT_HELPER._plot_fibers(verts)
    PLOT_HELPER.show_plot()
    
def test_plot_zones():
    list_of_union_zones = list(reversed(ANNOTATION_HELPER.get_final_zones_for_plotting([0, 20, 40, 60, 80])))
    PLOT_HELPER._plot_zones(list_of_union_zones)
    PLOT_HELPER.show_plot()

def test_plot_overlay():
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    annos = ANNOTATION_HELPER.annotations
    list_of_union_zones = list(reversed(ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150])))
    
    PLOT_HELPER.plot_final_overlay(verts, annos, list_of_union_zones) # Annotations on Bottom 
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    
    # TODO: NEED TO TEST WITH ANNOTATIONS ON TOP
    
    PLOT_HELPER.plot_final_overlay(verts, annos, list_of_union_zones, save_plot_as_img='boobies.tif')
    PLOT_HELPER.show_plot()

############ MANUAL PLOTTING/PLOT_HELPER TESTS: ############
# test_plot_annotations()
# test_plot_annotations_of_correct_name()
# test_plot_annotations_with_indexes()
# test_plot_fibers()
# test_plot_zones()
# test_plot_overlay()
############ MANUAL PLOTTING/PLOT_HELPER TESTS: ############


def test_draw_annotations():
    DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations, draw_anno_indexes = False)
    DRAW_HELPER.save_file_overlay('images/penis.tif')

def test_draw_annotations_with_indexes():
    DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.get_specific_annotations(['Ignore']),  draw_anno_indexes=True)
    DRAW_HELPER.save_file_overlay('images/penis.tif')

def test_draw_fibers():
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    DRAW_HELPER.draw_fibers(verts, widths)
    DRAW_HELPER.save_file_overlay('images/penis.tif')

def test_all_draw_fibers():
    verts = CTF_OUTPUT.get_fiber_vertices()
    widths = CTF_OUTPUT.get_fiber_widths()
    DRAW_HELPER.draw_fibers(verts, widths)
    DRAW_HELPER.save_file_overlay('images/penis.tif')

def test_draw_zones():
    zones = list(reversed(ANNOTATION_HELPER.get_final_zones([0, 20, 40, 60, 80])))
    to_draw = np.arange(len(zones))
    DRAW_HELPER.draw_zones(zones, to_draw=to_draw)
    DRAW_HELPER.save_file_overlay('images/penis.tif')
    
def test_draw_overlay():
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    zones = list(reversed(ANNOTATION_HELPER.get_final_zones([0, 50, 150])))
    draw_functions = [
        lambda: DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False),
        lambda: DRAW_HELPER.draw_fibers(verts, widths),
        lambda: DRAW_HELPER.draw_zones(zones, to_draw=[0, 1, 2, 3])
    ]

    DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False),
    DRAW_HELPER.draw_fibers(verts, widths),
    DRAW_HELPER.draw_zones(zones, to_draw=[0, 1, 2, 3])
    DRAW_HELPER.save_file_overlay()

############ MANUAL DRAWING/DRAW_HELPER TESTS: ############
# test_draw_annotations()
# test_draw_annotations_with_indexes()
# test_draw_fibers()
# test_all_draw_fibers()
test_draw_zones()
test_plot_zones()

# test_draw_overlay()
############ MANUAL DRAWING/DRAW_HELPER TESTS: ############

def test_draw_fibers_per_zone_single_zone():
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()

    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.annotations)    
    DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False)

    zones = list(reversed(ANNOTATION_HELPER.get_final_zones([0, 50, 150])))
    DRAW_HELPER.draw_zones(zones, to_draw=[1, 2])
    
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    DRAW_HELPER.draw_fibers_per_zone(verts, widths, bucketed_fibers, [1, 2])

    final_path = os.path.join(sys.path[0], 'images/penis.tif')
    composite_image = Image.alpha_composite(DRAW_HELPER.image, DRAW_HELPER.rgbimg)
    composite_image.save(final_path)

def test_draw_fibers_per_zone_single_zone_only_dcis():
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()

    # DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations, 'bongbong.tif', draw_anno_indexes = False)
    zones = list(reversed(ANNOTATION_HELPER.get_final_zones([0, 50, 150], ['DCIS'])))
    DRAW_HELPER.draw_zones(zones, to_draw=[0,1,2,3])

    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.get_specific_annotations(['DCIS']))    
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    DRAW_HELPER.draw_fibers_per_zone(verts, widths, bucketed_fibers, [0, 3])

    final_path = os.path.join(sys.path[0], 'images/penis.tif')
    composite_image = Image.alpha_composite(DRAW_HELPER.image, DRAW_HELPER.rgbimg)
    composite_image.save(final_path)

def test_plot_fibers_per_zone_single_zone():
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()

    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.annotations)
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    for i in range(4):
        PLOT_HELPER._plot_fibers_per_zone(verts, bucketed_fibers, [i])
        list_of_union_zones = list(reversed(ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150])))
        PLOT_HELPER._plot_zones(list_of_union_zones)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()
    
def test_plot_fibers_per_zone_single_zone_only_dcis():
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()

    specific_annos = ANNOTATION_HELPER.get_specific_annotations(['DCIS'])
    bucketed_fibers = bucket_the_fibers(fibers, centroids, specific_annos)
    verts = CTF_OUTPUT.get_fiber_vertices_thresholded()
    for i in range(4):
        PLOT_HELPER._plot_fibers_per_zone(verts, bucketed_fibers, [i])
        list_of_union_zones = list(reversed(ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150], ['DCIS'])))
        PLOT_HELPER._plot_zones(list_of_union_zones)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

############## TEST Plotting/Drawing per zone  ########
# test_draw_fibers_per_zone_single_zone()
# test_draw_fibers_per_zone_single_zone_only_dcis()
# test_plot_fibers_per_zone_single_zone()
# test_plot_fibers_per_zone_single_zone_only_dcis()
############## TEST Plotting/Drawing per zone  ########
def test_getting_averages():
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()
    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.annotations)
    values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
    
    print("AVERAGE WIDTH")
    widths = CTF_OUTPUT.get_fiber_widths()
    width_avgs = get_average_width_per_zone(widths, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} width averages: {width_avgs[i]}", 'green')
        
    print("AVERAGE LENGTHS")
    lengths = CTF_OUTPUT.get_fiber_lengths_thresholded()
    len_avgs = get_average_length_per_zone(lengths, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} length averages: {len_avgs[i]}", 'yellow')
        
    print("AVERAGE Angles")
    angles = CTF_OUTPUT.get_fiber_angles()
    len_avgs = get_average_angle_per_zone(angles, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} angle averages: {len_avgs[i]}", 'magenta')

def test_get_signal_densities():
    values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()

    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.annotations)
    print(bucketed_fibers.shape)
    
    print("SIGNAL DENSITIES")
    lengths = CTF_OUTPUT.get_fiber_lengths_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150]) 
    sig_dens = get_signal_density_overall(lengths, widths, final_union_of_zones, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')

def test_get_signal_densities_only_dcis():
    values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()
    
    ANNOTATION_HELPER.get_specific_annotations(['DCIS'])
    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.get_specific_annotations(['DCIS']))
    print(bucketed_fibers.shape)
    
    print("SIGNAL DENSITIES")
    lengths = CTF_OUTPUT.get_fiber_lengths_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150], ['DCIS']) 
    sig_dens = get_signal_density_overall(lengths, widths, final_union_of_zones, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')
        
def test_get_signal_density_only_in_stromal_region():
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()
    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.annotations)
    
    lengths = CTF_OUTPUT.get_fiber_lengths_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150])
     
    singnal_dens_only_stromal = get_singal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [1,2,3])
    cprint(f"Singal Density Stromal: {singnal_dens_only_stromal}", 'magenta')

def test_get_signal_density_per_annotation():
    fibers = CTF_OUTPUT.get_fiber_vertices_thresholded()
    centroids = CTF_OUTPUT.get_centroids()
    bucketed_fibers = bucket_the_fibers(fibers, centroids, ANNOTATION_HELPER.annotations)
    
    lengths = CTF_OUTPUT.get_fiber_lengths_thresholded()
    widths = CTF_OUTPUT.get_fiber_widths_thresholded()
    # For the 2nd annotation
    sig_dens = get_signal_density_per_annotation(bucketed_fibers[:, 1], ANNOTATION_HELPER.annotations[1], lengths, widths)
    
    print(f"FINAL Sig Dens: {sig_dens}")


############## TEST Signal_Densities and Averages per zone  ########
# test_getting_averages()
# test_get_signal_densities()
# test_get_signal_densities_only_dcis()
# test_get_signal_density_only_in_stromal_region()
# test_get_signal_density_per_annotation()
############## TEST Signal_Densities and Averages per zone  ########
