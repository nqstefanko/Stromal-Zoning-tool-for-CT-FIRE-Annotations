from ctfire_output_helper import CTFIREOutputHelper
from annotation_helper import AnnotationHelper
from test_export import *
from termcolor import cprint, colored

import dcis_utils as du
# CROPPED_IMG DATA CROP 2
TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.tif"
MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout_2B_D9_crop2.mat"
EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.geojson"

# With additional annotation
# EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\Copy Stuff\2B_D9_crop2_extra_anno.geojson"

# # # # CROPPED_IMG DATA CROP 1
# TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop1.tif"
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout_2B_D9_crop1.mat"
# EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop1.geojson"

#16 DENOISED DATA 16
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-016_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-016_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\ctFIREout\ctFIREout_DCIS-016_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

#18 DENOISED DATA 18
EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-018_10x10_1_Nuclei_Collagen - Denoised.geojson")
TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-018_10x10_1_Nuclei_Collagen - Denoised.tif")
MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\ctFIREout_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

with Image.open(TIF_FILEPATH) as img:
    IMG_DIMS = img.size

CTF_OUTPUT = CTFIREOutputHelper(MAT_FILEPATH)
DRAW_HELPER = DrawingHelper(TIF_FILEPATH)
ANNOTATION_HELPER = AnnotationHelper(EXPORTED_ANNOTATION_FILEPATH, IMG_DIMS)
PLOT_HELPER = PlottingHelper(tif_file=TIF_FILEPATH)

plot_tests = True
draw_tests = True
zone_tests = True
nums_tests = True
gui_tests  = True

if plot_tests:
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
        
        PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.get_specific_annotations(['Ignore']))
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_annotations_with_indexes():
        PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations, plot_anno_indexes=True)
        PLOT_HELPER.show_plot()

    def test_plot_fibers():
        
        # PLOT_HELPER._plot_fibers(CTF_OUTPUT.fibers)
        fibers = du.generate_fibers(10, 125, 175)
        PLOT_HELPER._plot_fibers(fibers)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()
        
        # all_verts = CTF_OUTPUT.get_fibers(0)
        # print(len(all_verts))
        # PLOT_HELPER._plot_fibers(all_verts)
        # PLOT_HELPER.show_plot()
             
    def test_plot_zones(zones=[0, 50, 150]):
        cprint("\nPlotting all zones...", 'cyan')
        list_of_union_zones = ANNOTATION_HELPER.get_final_zones_for_plotting(zones)
        PLOT_HELPER._plot_zones(list_of_union_zones)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_anno_zones(zones=[0, 50, 150]):
        for i in range(4):
            list_of_union_zones = ANNOTATION_HELPER.get_zones_per_annotation(zones, i)
            PLOT_HELPER._plot_zones(list_of_union_zones)
            PLOT_HELPER.show_plot()
            PLOT_HELPER.reset() 
        
    def test_plot_specific_zones(zones=[0, 50, 150], to_plot=[1, 3]):
        cprint("\nPlotting just zones 1, 3 zones...", 'cyan')
        list_of_union_zones = ANNOTATION_HELPER.get_final_zones_for_plotting(zones)
        PLOT_HELPER._plot_zones(list_of_union_zones, to_plot)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_overlay():
        annos = ANNOTATION_HELPER.annotations
        list_of_union_zones = ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150])
        
        cprint("\nPlotting all entire overlay without saving...", 'cyan')
        PLOT_HELPER.plot_final_overlay(CTF_OUTPUT.fibers, annos, list_of_union_zones) # Annotations on Bottom 
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()
        
        # TODO: NEED TO TEST WITH ANNOTATIONS ON TOP
        file_to_save = "images/greentea.tif"
        cprint(f"\nPlotting all entire overlay with saving to {file_to_save}...", 'cyan')
        PLOT_HELPER.plot_final_overlay(CTF_OUTPUT.fibers, annos, list_of_union_zones, save_plot_as_img=file_to_save)
        PLOT_HELPER.show_plot()

    ############ MANUAL PLOTTING/PLOT_HELPER TESTS: ############
    # test_plot_annotations()
    # test_plot_annotations_of_correct_name()
    # test_plot_annotations_with_indexes()
    # test_plot_fibers()
    # test_plot_zones()
    # test_plot_anno_zones()
    # test_plot_specific_zones()
    # test_plot_overlay()
    ############ MANUAL PLOTTING/PLOT_HELPER TESTS: ############

if draw_tests:
    def test_draw_annotations():
        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations, draw_anno_indexes = False)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_annotations_with_indexes():
        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.get_specific_annotations(['Ignore']),  draw_anno_indexes=True)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_fibers():
        DRAW_HELPER.draw_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_all_draw_fibers():
        verts = CTF_OUTPUT.get_fibers(0)
        widths = CTF_OUTPUT.get_fiber_widths(0)
        DRAW_HELPER.draw_fibers(verts, widths)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_zones():
        zones = ANNOTATION_HELPER.get_final_zones([0, 25, 50, 100])
        # zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150])
        DRAW_HELPER.draw_zones(zones)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_specific_zones(to_draw=[]):
        zones = ANNOTATION_HELPER.get_final_zones([0, 25, 50, 100])
        # zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150])
        DRAW_HELPER.draw_zones(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_zone_outlines():
        zones = ANNOTATION_HELPER.get_final_zones([0, 25, 50, 100])
        # zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150])
        DRAW_HELPER.draw_zone_outlines(zones)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_zone_outlines_specific(to_draw=[]):
        zones = ANNOTATION_HELPER.get_final_zones([0, 25, 50, 100])
        # zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150])
        DRAW_HELPER.draw_zone_outlines(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
        
    def test_draw_overlay():
        zones = list(reversed(ANNOTATION_HELPER.get_final_zones([0, 50, 150])))
        # Can pass these functions into save_file_overlay as well
        draw_functions = [
            lambda: DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False),
            lambda: DRAW_HELPER.draw_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths),
            lambda: DRAW_HELPER.draw_zone_outlines(zones, to_draw=[0, 1, 2, 3])
        ]

        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False),
        DRAW_HELPER.draw_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths),
        DRAW_HELPER.draw_zone_outlines(zones, to_draw=[0, 1, 2, 3])
        
        DRAW_HELPER.save_file_overlay()

    ############ MANUAL DRAWING/DRAW_HELPER TESTS: ############
    # test_draw_annotations()
    # test_draw_annotations_with_indexes()
    # test_draw_fibers()
    # test_all_draw_fibers()
    # test_draw_zones()
    # test_draw_specific_zones([1,2,3])
    # test_draw_specific_zones([0,3])
    # test_draw_specific_zones([0,1,2])
    # test_draw_specific_zones([1,3])
    # test_draw_specific_zones([1,2])
    # test_draw_zone_outlines()
    # test_draw_zone_outlines_specific([1,3])
    # test_draw_zone_outlines_specific([0,2])
    # test_draw_zone_outlines_specific([0,1,2])
    # test_draw_overlay()
    ############ MANUAL DRAWING/DRAW_HELPER TESTS: ############
    # test_plot_zones([0, 25, 50, 100])
    # test_plot_specific_zones([0, 25, 50, 100], [1,2])
    ###############

if zone_tests:
    def test_draw_fibers_per_zone_single_zone():
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False)

        zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150])
        # zones_to_draw = [1,2]
        zones_to_draw = [0,3]
        
        DRAW_HELPER.draw_zone_outlines(zones, zones_to_draw)
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, bucketed_fibers, zones_to_draw)

        final_path = os.path.join(sys.path[0], 'images/coffee.tif')
        composite_image = Image.alpha_composite(DRAW_HELPER.image, DRAW_HELPER.rgbimg)
        composite_image.save(final_path)

    def test_draw_fibers_per_zone_single_zone_only_dcis():
        # DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations, draw_anno_indexes = False)
        zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150], ['DCIS'])
        DRAW_HELPER.draw_zone_outlines(zones)

        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.get_specific_annotations(['DCIS']))    
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, bucketed_fibers, [0, 3])

        final_path = os.path.join(sys.path[0], 'images/coffee.tif')
        composite_image = Image.alpha_composite(DRAW_HELPER.image, DRAW_HELPER.rgbimg)
        composite_image.save(final_path)

    def test_plot_specific_zones():
        list_of_union_zones = ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150], ['DCIS',  'Atypia'])
        PLOT_HELPER._plot_zones(list_of_union_zones)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_fibers_per_zone_single_zone():
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)
        for i in range(4):
            PLOT_HELPER._plot_fibers_per_zone(CTF_OUTPUT.fibers, bucketed_fibers, [i])
            list_of_union_zones = ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150])
            PLOT_HELPER._plot_zones(list_of_union_zones)
            PLOT_HELPER.show_plot()
            PLOT_HELPER.reset()
        
    def test_plot_fibers_per_zone_single_zone_only_dcis():
        specific_annos = ANNOTATION_HELPER.get_specific_annotations(['DCIS'])
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, specific_annos)
        for i in range(4):
            PLOT_HELPER._plot_fibers_per_zone(CTF_OUTPUT.fibers, bucketed_fibers, [i])
            list_of_union_zones = ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150], ['DCIS'])
            PLOT_HELPER._plot_zones(list_of_union_zones)
            PLOT_HELPER.show_plot()
            PLOT_HELPER.reset()

    ############## TEST Plotting/Drawing per zone  ########
    # test_draw_fibers_per_zone_single_zone()
    # test_draw_fibers_per_zone_single_zone_only_dcis()
    # test_plot_specific_zones()
    # test_plot_fibers_per_zone_single_zone()
    # test_plot_fibers_per_zone_single_zone_only_dcis()
    ############## TEST Plotting/Drawing per zone  ########

if nums_tests:
    # NEED TO CHECK
    def test_getting_averages():
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)
        values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
        
        width_avgs = get_average_value_per_zone(CTF_OUTPUT.fiber_widths, bucketed_fibers)
        for i in range(4):
            cprint(f"{values[i]} width averages: {width_avgs[i]}", 'green')
            
        print("AVERAGE LENGTHS")
        len_avgs = get_average_value_per_zone(CTF_OUTPUT.get_fiber_lengths(), bucketed_fibers)
        for i in range(4):
            cprint(f"{values[i]} length averages: {len_avgs[i]}", 'yellow')
            
        print("AVERAGE Angles")
        len_avgs = get_average_value_per_zone(CTF_OUTPUT.fiber_angles, bucketed_fibers)
        for i in range(4):
            cprint(f"{values[i]} angle averages: {len_avgs[i]}", 'magenta')

    def test_get_signal_densities():
        values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
        
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)
        print(bucketed_fibers.shape)
        
        print("SIGNAL DENSITIES")
        final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150]) 
        sig_dens = get_signal_density_overall(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths,
                                              final_union_of_zones, bucketed_fibers)
        for i in range(4):
            cprint(f"{values[i]} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')

    def test_get_signal_densities_with_controlled_fibers():
        values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
        fibers_anno1 = du.generate_fibers(15, 125, 175)
        bucketed_fibers = bucket_the_fibers(fibers_anno1, CTF_OUTPUT.get_centroids(fibers_anno1), ANNOTATION_HELPER.annotations)
        print(bucketed_fibers.shape)
        
        final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150]) 
        sig_dens = get_signal_density_overall(du.get_test_fiber_lengths_from_fibers(fibers_anno1), 
                                              du.get_test_fibers_widths(len(fibers_anno1)),
                                              final_union_of_zones, bucketed_fibers)
        for i in range(4):
            cprint(f"{values[i]} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')
            PLOT_HELPER._plot_fibers_per_zone(fibers_anno1, bucketed_fibers, [i])
            list_of_union_zones = ANNOTATION_HELPER.get_final_zones_for_plotting([0, 50, 150])
            PLOT_HELPER._plot_zones(list_of_union_zones)
            PLOT_HELPER.show_plot()
            PLOT_HELPER.reset()
        
    def test_get_signal_density_diff_zones():
        zones = [0,25,50,150]
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations, zones)
        print(bucketed_fibers.shape)

        final_union_of_zones = ANNOTATION_HELPER.get_final_zones(zones)
        sig_dens = get_signal_density_overall(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, final_union_of_zones, bucketed_fibers)

        print("SIGNAL DENSITIES")
        for i in range(len(zones) + 1):
            cprint(f"Zone {i} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')
    
    def test_get_signal_densities_only_dcis():
        values = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]
        
        ANNOTATION_HELPER.get_specific_annotations(['DCIS'])
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids,  ANNOTATION_HELPER.get_specific_annotations(['DCIS']))
        print(bucketed_fibers.shape)
        
        print("SIGNAL DENSITIES")
        final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150], ['DCIS']) 
        sig_dens = get_signal_density_overall(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, final_union_of_zones, bucketed_fibers)
        for i in range(4):
            cprint(f"{values[i]} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')
            
    def test_get_signal_density_only_in_stromal_region():
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)

        lengths = CTF_OUTPUT.get_fiber_lengths()
        widths = CTF_OUTPUT.fiber_widths
        final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 50, 150])
        
        singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths,
                                                                         final_union_of_zones, bucketed_fibers, [1,2,3])
        cprint(f"Singal Density Stromal:{'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')

        singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [0,1,2,3])
        cprint(f"Singal Density Stromal:{'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')

    def test_get_signal_density_only_in_stromal_region_diff_zones():
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)

        lengths = CTF_OUTPUT.get_fiber_lengths()
        widths = CTF_OUTPUT.fiber_widths
        final_union_of_zones = ANNOTATION_HELPER.get_final_zones([0, 25, 50, 100])
        
        singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [1,2,3,4])
        cprint(f"Singal Density Stromal: {'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')

        singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [0,1,2,3])
        cprint(f"Singal Density Stromal: {'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')
        
        singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [0,1,2,3,4])
        cprint(f"Singal Density Stromal: {'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')

    def test_get_signal_density_per_annotation():
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)

        
        lengths = CTF_OUTPUT.get_fiber_lengths()
        widths = CTF_OUTPUT.fiber_widths()
        # For the 2nd annotation
        sig_dens = get_signal_density_per_annotation(bucketed_fibers[:, 1], ANNOTATION_HELPER.annotations[1], lengths, widths)
        cprint(f"Singal Density For Annotation:{'{0:.2%}'.format(sig_dens)}", 'cyan')
        
    def test_get_signal_density_for_all_annotations():
        bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)

        # For the 2nd annotation
        lengths  = CTF_OUTPUT.get_fiber_lengths()
        widths = CTF_OUTPUT.fiber_widths()
        sig_dens = get_signal_density_for_all_annotations(bucketed_fibers, ANNOTATION_HELPER.annotations, lengths, widths)
        cprint(f"Singal Density For Annotation:{sig_dens}", 'cyan')
    
    ############## TEST Signal_Densities and Averages per zone  ########
    # test_getting_averages()
    # test_get_signal_densities()
    # test_get_signal_density_diff_zones()
    # test_get_signal_densities_only_dcis()
    # test_get_signal_density_only_in_stromal_region()
    # test_get_signal_densities_with_controlled_fibers()
    # test_get_signal_density_only_in_stromal_region_diff_zones()
    # test_get_signal_density_per_annotation()
    # test_get_signal_density_for_all_annotations()
    ############## TEST Signal_Densities and Averages per zone  ########

# Going into bucket_the_fibers at time 2023-04-05 11:45:37.615937
# Done with bucket_the_fibers in 0.04603886604309082 sec
# AVERAGE WIDTH
# DCIS width averages: 5.104434415157757
# Epithelial width averages: 5.48217150834001
# Mid-Stromal width averages: 4.780031617139728
# Other Stromal width averages: 5.936376892030239
# AVERAGE LENGTHS
# DCIS length averages: 55.714408846475
# Epithelial length averages: 65.51393442761696
# Mid-Stromal length averages: 69.2364216866566
# Other Stromal length averages: 57.008707779816085
# AVERAGE Angles
# DCIS angle averages: 0.4512225724506418
# Epithelial angle averages: 0.43378574859583996
# Mid-Stromal angle averages: 0.5389311076343537
# Other Stromal angle averages: 1.1902899496825317


# DCIS signal density: 20.62%
# Epithelial signal density: 20.48%
# Mid-Stromal signal density: 16.49%
# Other Stromal signal density: 12.97%

# Zone 0 signal density: 20.62%
# Zone 1 signal density: 27.83%
# Zone 2 signal density: 10.62%
# Zone 3 signal density: 11.81%
# Zone 4 signal density: 26.27%


if gui_tests:
    pass