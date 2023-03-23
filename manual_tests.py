from ctfire_output_helper import CTFIREOutputHelper
from annotation_helper import AnnotationHelper
from test_export import *
from termcolor import cprint, colored

# #CROPPED_IMG DATA
TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.tif"
MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout\ctFIREout_2B_D9_crop2.mat"
EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.geojson"

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
ANNOTATION_HELPER = AnnotationHelper(EXPORTED_ANNOTATION_FILEPATH, IMG_DIMS)

PLOT_HELPER = PlottingHelper(CTF_OUTPUT, ANNOTATION_HELPER, tif_file=TIF_FILEPATH)
DRAW_HELPER = DrawingHelper(CTF_OUTPUT, ANNOTATION_HELPER, TIF_FILEPATH)

# plt.ion()

def test_plot_annotations():
    PLOT_HELPER._plot_annotations()
    PLOT_HELPER.show_plot()

def test_plot_annotations_with_indexes():
    PLOT_HELPER._plot_annotations(True)
    PLOT_HELPER.show_plot()

def test_plot_fibers():
    PLOT_HELPER._plot_fibers()
    PLOT_HELPER.show_plot()

def test_plot_zones():
    PLOT_HELPER._plot_zones()
    PLOT_HELPER.show_plot()

def test_plot_overlay():
    PLOT_HELPER.plot_final_overlay() # Annotations on Bottom 
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    
    # TODO: NEED TO TEST WITH ANNOTATIONS ON TOP
    
    PLOT_HELPER.plot_final_overlay(save_plot_as_img='boobies.tif')
    PLOT_HELPER.show_plot()

def test_plot_zones_with_overlay():
    PLOT_HELPER._plot_zones()
    PLOT_HELPER.plot_final_overlay() # Annotations on Bottom 
    PLOT_HELPER.show_plot()

def test_plot_annotations_only_dcis():
    PLOT_HELPER._plot_annotations(['DCIS'])
    PLOT_HELPER.show_plot()
    PLOT_HELPER.reset()
    PLOT_HELPER._plot_annotations(['Ignore'])
    PLOT_HELPER.show_plot()
    
############ MANUAL PLOTTING/PLOT_HELPER TESTS: ############
# test_plot_annotations()
# test_plot_annotations_with_indexes()
# test_plot_fibers()
# test_plot_zones()
# test_plot_overlay()
# test_plot_zones_with_overlay()
# test_plot_annotations_of_correct_name()
############ MANUAL PLOTTING/PLOT_HELPER TESTS: ############


def test_draw_annotations():
    DRAW_HELPER._draw_annotations('bongbong.tif', True)

def test_draw_annotations_with_indexes():
    DRAW_HELPER._draw_annotations('bongbong.tif')

def test_draw_fibers():
    DRAW_HELPER.draw_fibers('bongbong.tif')

def test_draw_zones():
    DRAW_HELPER.draw_zones(final_path_to_save='bongbong.tif', to_draw=[1, 2, 3])

def test_draw_overlay_no_zones_anno_on_top():
    DRAW_HELPER.save_final_overlay()

def test_draw_overlay_no_zones_anno_on_bottom():
    DRAW_HELPER.save_final_overlay(False)
    
def test_draw_overlay_with_zones():
    DRAW_HELPER.save_final_overlay(with_zones=True)
    
############ MANUAL DRAWING/DRAW_HELPER TESTS: ############
# test_draw_annotations()
# test_draw_annotations_with_indexes()
# test_draw_fibers()
# test_draw_zones()
# test_draw_overlay_no_zones_anno_on_top()
# test_draw_overlay_no_zones_anno_on_bottom()
# test_draw_overlay_with_zones()
############ MANUAL DRAWING/DRAW_HELPER TESTS: ############


def test_draw_fibers_per_zone_single_zone():
    bucketed_fibers = bucket_the_fibers(CTF_OUTPUT, ANNOTATION_HELPER)
    print(bucketed_fibers.shape)
    DRAW_HELPER._draw_annotations()
    DRAW_HELPER.draw_zones(to_draw=[0, 1])
    
    DRAW_HELPER.draw_fibers_per_zone(bucketed_fibers, [0, 3])

    final_path = os.path.join(sys.path[0], 'boob.tif')
    composite_image = Image.alpha_composite(DRAW_HELPER.image, DRAW_HELPER.rgbimg)
    composite_image.save(final_path)

# test_draw_fibers_per_zone_single_zone()


def test_plot_fibers_per_zone_single_zone():
    bucketed_fibers = bucket_the_fibers(CTF_OUTPUT, ANNOTATION_HELPER)
    PLOT_HELPER._plot_fibers_per_zone(bucketed_fibers, [1])
    PLOT_HELPER._plot_zones()
    PLOT_HELPER.show_plot()
    
# test_plot_fibers_per_zone_single_zone()

def test_get_signal_densities():
    values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
    bucketed_fibers = bucket_the_fibers(CTF_OUTPUT, ANNOTATION_HELPER)
    print(bucketed_fibers.shape)
    
    print("SIGNAL DENSITIES")
    sig_dens = get_signal_density_overall(CTF_OUTPUT, ANNOTATION_HELPER, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')

# test_get_signal_densities()

def test_getting_averages():
    bucketed_fibers = bucket_the_fibers(CTF_OUTPUT, ANNOTATION_HELPER)
    values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
    
    print("AVERAGE WIDTH")
    width_avgs = get_average_width_per_zone(CTF_OUTPUT, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} width averages: {width_avgs[i]}", 'green')
        
    print("AVERAGE LENGTHS")
    len_avgs = get_average_length_per_zone(CTF_OUTPUT, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} length averages: {len_avgs[i]}", 'yellow')
        
    print("AVERAGE Angles")
    len_avgs = get_average_angle_per_zone(CTF_OUTPUT, bucketed_fibers)
    for i in range(4):
        cprint(f"{values[i]} angle averages: {len_avgs[i]}", 'magenta')

# test_getting_averages()