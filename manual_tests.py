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

# # # # # CROPPED_IMG DATA CROP 1
# TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop1.tif"
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout_2B_D9_crop1.mat"
# EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop1.geojson"

#16 DENOISED DATA 16
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-016_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-016_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\ctFIREout\ctFIREout_DCIS-016_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

# # #18 DENOISED DATA 18
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-018_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-018_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\ctFIREout_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

with Image.open(TIF_FILEPATH) as img:
    IMG_DIMS = img.size

CTF_OUTPUT = CTFIREOutputHelper(MAT_FILEPATH)
DRAW_HELPER = DrawingHelper(TIF_FILEPATH)
ANNOTATION_HELPER = AnnotationHelper(EXPORTED_ANNOTATION_FILEPATH, IMG_DIMS)
PLOT_HELPER = PlottingHelper(tif_file=TIF_FILEPATH)
VALUES = ["DCIS", "Epithelial", "Mid-Stromal", "Other Stromal"]

plot_tests = True
draw_tests = True
zone_tests = True
nums_tests = True
crunch_tests = True
gui_tests  = True

if plot_tests:
    def test_plot_annotations():
        PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()
        
        PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.get_annotations_from_indexes())
        PLOT_HELPER.show_plot()

    def test_plot_annotations_of_correct_name():
        PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.get_annotations_from_indexes(ANNOTATION_HELPER.get_annotation_indexes(['DCIS'])))
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()
        
        PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.get_annotations_from_indexes(ANNOTATION_HELPER.get_annotation_indexes(['Ignore'])))
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_annotations_with_annotation_info():
        PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations, plot_anno_indexes=True)
        PLOT_HELPER.show_plot()

    def test_plot_fibers():        
        # fibers = du.generate_fibers(10, 125, 175) # 10 Fibers in 125 to 175 pixel range
        # PLOT_HELPER._plot_fibers(fibers)
        
        PLOT_HELPER._plot_fibers(CTF_OUTPUT.fibers)
        print(len(CTF_OUTPUT.fibers))
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()
        
        all_verts = CTF_OUTPUT.get_fibers(0)
        print(len(all_verts))
        PLOT_HELPER._plot_fibers(all_verts)
        PLOT_HELPER.show_plot()
             
    def test_plot_all_zones(zones=[0, 100, 150]):
        cprint(f"\nPlotting all zones {zones}...", 'cyan')
        list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting(zones, [])
        PLOT_HELPER._plot_zones(list_of_union_zones)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()
    
    def test_plot_all_crunched_zone(zones=[0, 150, 200], annos=[0]):
        cprint("\nPlotting all zones...", 'cyan')
        # PLOT_HELPER._plot_annotations(ANNOTATION_HELPER.annotations, plot_anno_indexes=True)
        list_of_union_zones = ANNOTATION_HELPER.get_zones_crunched_for_plotting(zones, annos, ANNOTATION_HELPER.get_annotation_indexes([]))
        PLOT_HELPER._plot_zones(list_of_union_zones)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_zones_for_each_anno(zones=[0, 50, 150]):
        for i in range(4):
            list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting(zones, [i])
            PLOT_HELPER._plot_zones(list_of_union_zones)
            PLOT_HELPER.show_plot()
            PLOT_HELPER.reset() 
        
    def test_plot_specific_zones(zones=[0, 50, 150], to_plot=[1, 3]):
        cprint("\nPlotting just zones 1, 3 zones...", 'cyan')
        list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting(zones)
        PLOT_HELPER._plot_zones(list_of_union_zones, to_plot)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_overlay():
        annos = ANNOTATION_HELPER.annotations
        list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting([0, 50, 150])
        
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
    # test_plot_annotations_with_annotation_info()
    # test_plot_fibers()
    # test_plot_all_zones(np.array([0, 25, 100, 200]))
    # test_plot_all_crunched_zone()
    # test_plot_all_crunched_zone()
    # test_plot_zones_for_each_anno()
    # test_plot_specific_zones()
    # test_plot_overlay()
    ############ MANUAL PLOTTING/PLOT_HELPER TESTS: ############

if draw_tests:
    def test_draw_annotations():
        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations, draw_anno_indexes = False)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_annotations_with_annotation_info():
        anno_indexes_to_draw = ANNOTATION_HELPER.get_annotation_indexes(['Ignore'])
        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes_to_draw),  draw_anno_indexes=True)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
    
    def test_draw_specific_annotations_with_annotation_info():
        anno_indexes_to_draw = ANNOTATION_HELPER.get_annotation_indexes(['Ignore', '0']) # Note Str 0 Here
        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes_to_draw),  draw_anno_indexes=True)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_fibers():
        # Note these are the thresholded fibers
        DRAW_HELPER.draw_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_all_draw_fibers():
        verts = CTF_OUTPUT.get_fibers(0) # Threshold at Zero, so it will be all fibers and widths
        widths = CTF_OUTPUT.get_fiber_widths(0)
        DRAW_HELPER.draw_fibers(verts, widths)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_all_zones():
        indexes = ANNOTATION_HELPER.get_annotation_indexes()
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 150, 200], indexes) # 
        DRAW_HELPER.draw_zones(zones)
        DRAW_HELPER.save_file_overlay('images/coffee5.tif')
            
    def test_draw_specific_zones(to_draw=[]):
        indexes = ANNOTATION_HELPER.get_annotation_indexes()    
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], indexes) #
        # zones = ANNOTATION_HELPER.get_final_union_zones([0, 25, 50, 150], []) # 
        DRAW_HELPER.draw_zones(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_all_zones_based_on_specific_annotations(to_draw=[]):
        # indexes = ANNOTATION_HELPER.get_annotation_indexes('0')    
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 150, 200], [0]) #
        # zones = ANNOTATION_HELPER.get_final_union_zones([0, 25, 50, 150], []) # 
        DRAW_HELPER.draw_zones(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_specific_zones_based_on_specific_annotations(to_draw=[]):
        indexes = ANNOTATION_HELPER.get_annotation_indexes('DCIS')    
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], indexes) #
        # zones = ANNOTATION_HELPER.get_final_union_zones([0, 25, 50, 150], []) # 
        DRAW_HELPER.draw_zones(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
        
        DRAW_HELPER.reset()
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], [1]) #
        DRAW_HELPER.draw_zones(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee2.tif')
        
    def test_draw_all_crunched_zone(zones=[0, 50, 150], indexes=[0]):
        zones = ANNOTATION_HELPER.get_zones_crunched(zones, indexes)
        DRAW_HELPER.draw_zones(zones)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
    
    def test_draw_specific_crunched_zone(zones=[0, 50, 150], indexes=[0], to_draw=[1,2]):
        zones = ANNOTATION_HELPER.get_zones_crunched(zones, indexes)
        DRAW_HELPER.draw_zones(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
    
    def test_draw_all_crunched_based_on_dcis(zones=[0, 50, 150], indexes=[1], to_base=[0,1], to_draw=[]):
        zones = ANNOTATION_HELPER.get_zones_crunched(zones, indexes, to_base)
        DRAW_HELPER.draw_zones(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
    def test_draw_zone_outlines():
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 25, 50, 150], ANNOTATION_HELPER.get_annotation_indexes()) # 
        DRAW_HELPER.draw_zone_outlines(zones)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_zone_outlines_specific(to_draw=[]):
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], ANNOTATION_HELPER.get_annotation_indexes())
        DRAW_HELPER.draw_zone_outlines(zones, to_draw)
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
            
    def test_draw_overlay():
        # zones = list(reversed(ANNOTATION_HELPER.get_final_zones([0, 50, 150])))
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], ANNOTATION_HELPER.get_annotation_indexes())
        
        # Can pass these functions into save_file_overlay as well
        draw_functions = [
            lambda: DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False),
            lambda: DRAW_HELPER.draw_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths),
            lambda: DRAW_HELPER.draw_zone_outlines(zones, to_draw=[0, 1, 2, 3])
        ]

        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations,  draw_anno_indexes = False),
        DRAW_HELPER.draw_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths),
        DRAW_HELPER.draw_zones(zones, to_draw=[0, 1, 2, 3])
        
        DRAW_HELPER.save_file_overlay()

    ############ MANUAL DRAWING/DRAW_HELPER TESTS: ############
    # test_draw_annotations()
    # test_draw_annotations_with_annotation_info()
    # test_draw_specific_annotations_with_annotation_info()
    
    # test_draw_fibers()
    # test_all_draw_fibers()
    
    # test_draw_all_zones() 
    # test_draw_specific_zones([0,1,2,3])
    # test_draw_all_zones_based_on_specific_annotations()
    # test_draw_specific_zones_based_on_specific_annotations(to_draw=[1,2])
    
    # test_draw_all_crunched_zone()
    # test_draw_all_crunched_zone([0, 150, 200])
    # test_draw_specific_crunched_zone(zones=[0, 50, 150], indexes=[1], to_draw=[1,2])
    # test_draw_all_crunched_based_on_dcis()
    
    # test_draw_zone_outlines()
    # test_draw_zone_outlines_specific([1,3])
    # test_draw_overlay()
    ############ MANUAL DRAWING/DRAW_HELPER TESTS: ############
    # test_plot_all_zones()
    # test_plot_specific_zones(to_plot=[1, 3])

if zone_tests:
    def test_draw_fibers_per_zone_single_zone():
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        bucketed_fibers = get_bucket_for_each_fiber(fiber_dists)
        list_union_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], ANNOTATION_HELPER.get_annotation_indexes())

        zones_to_draw = [0, 1,2, 3]
        # zones_to_draw = [0,3]
        
        DRAW_HELPER.draw_zones(list_union_zones, zones_to_draw)
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, bucketed_fibers, zones_to_draw)

        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_fibers_per_zone_single_zone_only_dcis():
        anno_indexes = ANNOTATION_HELPER.get_annotation_indexes(['DCIS'])
        list_union_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], anno_indexes)
           
        zones_to_draw = [3]
        DRAW_HELPER.draw_zones(list_union_zones, zones_to_draw)
        
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        bucketed_fibers = get_bucket_for_each_fiber(fiber_dists[:, anno_indexes])
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, bucketed_fibers, zones_to_draw)

        DRAW_HELPER.save_file_overlay('images/coffee.tif')

    def test_draw_fiber_per_zone_crunched():
                # DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations, draw_anno_indexes = False)\
        anno_indexes = [0] #ANNOTATION_HELPER.get_annotation_indexes([21])
        zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], anno_indexes)
        zones = ANNOTATION_HELPER.get_zones_crunched([0, 50, 150], anno_indexes)
        DRAW_HELPER.draw_zones(zones)

        bucketed_fibers, other_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, 
                                                          ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes))    
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, bucketed_fibers, [1])
        
        # DRAW_HELPER.draw_fibers_per_zone_crunched2(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, other_fibers, anno_indexes, [1,2])
        DRAW_HELPER.save_file_overlay('images/coffee5.tif')
    
    def test_plot_specific_zones():
        anno_indexes = ANNOTATION_HELPER.get_annotation_indexes(['DCIS'])
        list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting([0, 50, 150], anno_indexes)
        PLOT_HELPER._plot_zones(list_of_union_zones)
        PLOT_HELPER.show_plot()
        PLOT_HELPER.reset()

    def test_plot_fibers_per_zone_single_zone():
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        bucketed_fibers = get_bucket_for_each_fiber(fiber_dists)
        
        for i in range(4):
            PLOT_HELPER._plot_fibers_per_zone(CTF_OUTPUT.fibers, bucketed_fibers, [i])
            anno_indexes = ANNOTATION_HELPER.get_annotation_indexes() # All
            list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting([0, 50, 150], anno_indexes)
            PLOT_HELPER._plot_zones(list_of_union_zones)
            PLOT_HELPER.show_plot()
            PLOT_HELPER.reset()
        
    def test_plot_fibers_per_zone_single_zone_only_dcis():
        anno_indexes = ANNOTATION_HELPER.get_annotation_indexes(['DCIS']) # All
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        bucketed_fibers = get_bucket_for_each_fiber(fiber_dists[:, anno_indexes])
        for i in range(4):
            PLOT_HELPER._plot_fibers_per_zone(CTF_OUTPUT.fibers, bucketed_fibers, [i])
            list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting([0, 50, 150], anno_indexes)
            PLOT_HELPER._plot_zones(list_of_union_zones)
            PLOT_HELPER.show_plot()
            PLOT_HELPER.reset()

    ############## TEST Plotting/Drawing per zone  ########
    test_draw_fibers_per_zone_single_zone()
    # test_draw_fibers_per_zone_single_zone_only_dcis()
    # test_draw_fiber_per_zone_crunched()
    # test_plot_specific_zones()
    # test_plot_fibers_per_zone_single_zone()
    # test_plot_fibers_per_zone_single_zone_only_dcis()
    ############## TEST Plotting/Drawing per zone  ########

if nums_tests:
    def test_getting_averages():
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        bucketed_fibers = get_bucket_for_each_fiber(fiber_dists)
        
        width_avgs = get_average_value_per_zone(CTF_OUTPUT.fiber_widths, bucketed_fibers)
        for i in range(4):
            cprint(f"{VALUES[i]} width averages: {width_avgs[i]}", 'green')
            
        print("AVERAGE LENGTHS")
        len_avgs = get_average_value_per_zone(CTF_OUTPUT.get_fiber_lengths(), bucketed_fibers)
        for i in range(4):
            cprint(f"{VALUES[i]} length averages: {len_avgs[i]}", 'yellow')
            
        print("AVERAGE Angles")
        len_avgs = get_average_value_per_zone(CTF_OUTPUT.fiber_angles, bucketed_fibers)
        for i in range(4):
            cprint(f"{VALUES[i]} angle averages: {len_avgs[i]}", 'magenta')

    def test_get_signal_density_crunched_zone():
        
        anno_indexes = ANNOTATION_HELPER.get_annotation_indexes(['DCIS']) # All
        annos_to_use = ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes)
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, annos_to_use)    
        fiber_dists_bucketed = get_bucket_for_each_fiber(fiber_dists)    
        
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, fiber_dists_bucketed)
        final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], anno_indexes)
        cprint(f"Getting signal density for Zones: [0, 50, 150]", 'yellow')
        for i in range(4):
            cprint(f"{VALUES[i]} signal density: {'{0:.2%}'.format(zone_sums[i] / final_union_of_zones[i].area)}", 'yellow')

    def test_draw_fibers_colors_per_zone():
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)   
        buckets=np.array([0, 50, 150])
        fibers_dists_buckted = np.digitize(np.min(fiber_dists, axis=1), buckets, right=True).astype(int)
        DRAW_HELPER.draw_fibers_colored_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, fibers_dists_buckted)
        DRAW_HELPER.draw_annotations(ANNOTATION_HELPER.annotations)

        DRAW_HELPER.save_file_overlay('images/coffee.tif')
        
    def test_get_signal_density_only_in_stromal_region():
        
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        fiber_dists_bucketed = get_bucket_for_each_fiber(fiber_dists)    
        
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, fiber_dists_bucketed)
        
        final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], ANNOTATION_HELPER.get_annotation_indexes())

        cprint(f"Getting signal density for All zones with buckets [0, 50, 150]", 'cyan')
        singnal_dens_only_stromal = get_signal_density_per_desired_zones(zone_sums, final_union_of_zones, [0,1,2,3])
        cprint(f"Singal Density ALL Zones:{'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')

        singnal_dens_only_stromal = get_signal_density_per_desired_zones(zone_sums, final_union_of_zones, [1,2,3])
        cprint(f"Singal Density Stromal:{'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')
        
        zones2 = np.array([0, 25, 100, 200])
        fiber_dists_bucketed = get_bucket_for_each_fiber(fiber_dists, zones2)    
        
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(
            CTF_OUTPUT.get_fiber_lengths(),
            CTF_OUTPUT.fiber_widths,
            fiber_dists_bucketed, 
            zones2
        )
        final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones(zones2, ANNOTATION_HELPER.get_annotation_indexes())

        cprint(f"Getting signal density for All zones with buckets{zones2}", 'magenta')
        singnal_dens_only_stromal = get_signal_density_per_desired_zones(zone_sums, final_union_of_zones, [0,1,2,3])
        cprint(f"Singal Density ALL Zones:{'{0:.2%}'.format(singnal_dens_only_stromal)}", 'magenta')

        singnal_dens_only_stromal = get_signal_density_per_desired_zones(zone_sums, final_union_of_zones, [1,2,3])
        cprint(f"Singal Density Stromal:{'{0:.2%}'.format(singnal_dens_only_stromal)}", 'magenta')
        
    def test_get_signal_density_per_annotation():
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        lengths = CTF_OUTPUT.get_fiber_lengths()
        widths = CTF_OUTPUT.fiber_widths
        for anno in ANNOTATION_HELPER.annotations:
            sig_dens = get_signal_density_per_annotation(fiber_dists[:, anno.original_index], anno, lengths, widths)
            cprint(f"Singal Density For Annotation {anno.original_index}: {'{0:.2%}'.format(sig_dens)}", 'cyan')
            
    def test_get_signal_density_for_all_annotations():
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        x = get_signal_density_for_all_annotations(fiber_dists, ANNOTATION_HELPER.annotations, CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths)
        cprint(f"Singal Density For Annotation:{x}", 'cyan')
    
    ############## TEST Signal_Densities and Averages per zone  ########
    # test_getting_averages()
    # test_get_fiber_density_and_counts_per_zone_for_every_annotation()
    # test_get_signal_density_only_dcis()
    # test_draw_fibers_colors_per_zone()
    # test_get_signal_density_only_in_stromal_region()
    # test_get_signal_density_per_annotation()
    # test_get_signal_density_for_all_annotations()
    ############## TEST Signal_Densities and Averages per zone  ########

if crunch_tests:
    def test_basic_crunch_with_fibers(buckets=np.array([0, 50, 150], dtype=int), indexes=[0,1,2]):
        crunched_union_zones = ANNOTATION_HELPER.get_zones_crunched(buckets, indexes)
        DRAW_HELPER.draw_zones(crunched_union_zones)
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    

        crunched_fibs = get_crunched_fibers(fiber_dists.astype(int), indexes, buckets=buckets)
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, crunched_fibs, [0])
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
        
        # Buckets
        # Indexes for Crunched Zones
        # BASE INDEXES CRUNCHED ZONE IF THIS IS PRESENT THEN 
        
        #Fiber Dists (IF BASE INDEXES IS PRESENT THEN All Fiber dists is based off of that!)
        # Crunched Fibers based on Indexes for crunched zones!
    
    def test_basic_crunch_with_new_base_fibers(buckets=np.array([0, 50, 150], dtype=int), indexes=[0]):
        crunched_union_zones = ANNOTATION_HELPER.get_zones_crunched(buckets, indexes, [0,1])
        DRAW_HELPER.draw_zones(crunched_union_zones)
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations[0:2])    

        crunched_fibs = get_crunched_fibers(fiber_dists.astype(int), indexes, buckets=buckets)
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, crunched_fibs, [3])
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
    
    def test_get_fiber_density_and_counts_per_zone_for_every_annotation():
        
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        fiber_dists_bucketed = get_bucket_for_each_fiber(fiber_dists)    
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, fiber_dists_bucketed)
        final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], ANNOTATION_HELPER.get_annotation_indexes())
        cprint(f"Getting signal density for Zones: [0, 50, 150]", 'yellow')
        for i in range(4):
            cprint(f"{VALUES[i]} signal density: {'{0:.2%}'.format(zone_sums[i] / final_union_of_zones[i].area)}", 'yellow')

        zones2 = np.array([0, 25, 100, 200])
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    
        fiber_dists_bucketed = get_bucket_for_each_fiber(fiber_dists, zones2)    
        
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(
            CTF_OUTPUT.get_fiber_lengths(),
            CTF_OUTPUT.fiber_widths,
            fiber_dists_bucketed, 
            zones2
        )
        final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones(zones2, ANNOTATION_HELPER.get_annotation_indexes())
        cprint(f"Getting signal density for Zones: {zones2}", 'cyan')
        for i in range(4):
            cprint(f"{VALUES[i]} signal density: {'{0:.2%}'.format(zone_sums[i] / final_union_of_zones[i].area)}", 'cyan')

    def test_get_signal_density_only_dcis():
        anno_indexes = ANNOTATION_HELPER.get_annotation_indexes(['DCIS']) # All
        annos_to_use = ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes)
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, annos_to_use)    
        fiber_dists_bucketed = get_bucket_for_each_fiber(fiber_dists)    
        
        list_union_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], anno_indexes)
        DRAW_HELPER.draw_zones(list_union_zones)
        
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, fiber_dists_bucketed, [0]) #Zones to draw missing
        DRAW_HELPER.save_file_overlay('images/coffee.tif')
        
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, fiber_dists_bucketed)
        print(zone_counts)
        final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], anno_indexes)
        cprint(f"Getting signal density for Zones: [0, 50, 150]", 'yellow')
        for i in range(4):
            cprint(f"{VALUES[i]} signal density: {'{0:.2%}'.format(zone_sums[i] / final_union_of_zones[i].area)}", 'yellow')

    def test_get_signal_density_crunched_zone(buckets=np.array([0, 50, 150], dtype=int), indexes=[0,1,2]):
        crunched_union_zones = ANNOTATION_HELPER.get_zones_crunched(buckets, indexes)
        DRAW_HELPER.draw_zones(crunched_union_zones)
        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)    

        crunched_fibs = get_crunched_fibers(fiber_dists.astype(int), indexes, buckets=buckets)
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, crunched_fibs, [2])  #Crunched or Bucketed
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, crunched_fibs)
        print(zone_counts, crunched_union_zones[0].area)
        cprint(f"Getting signal density for Zones: [0, 50, 150]", 'yellow')
        for i in range(4):
            cprint(f"{VALUES[i]} signal density: {'{0:.2%}'.format(zone_sums[i] / crunched_union_zones[i].area)}", 'yellow')

    def test_get_signal_density_crunched_zone_with_new_base(buckets=np.array([0, 50, 150], dtype=int), indexes=[0]):
        crunched_union_zones = ANNOTATION_HELPER.get_zones_crunched(buckets, indexes, [0,1])
        DRAW_HELPER.draw_zones(crunched_union_zones)

        fiber_dists = get_all_fiber_dists_for_each_anno(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations[0:2])    
        crunched_fibs = get_crunched_fibers(fiber_dists.astype(int), indexes, buckets=buckets)
        DRAW_HELPER.draw_fibers_per_zone(CTF_OUTPUT.fibers, CTF_OUTPUT.fiber_widths, crunched_fibs, [1])  #Crunched or Bucketed
        DRAW_HELPER.save_file_overlay('images/coffee.tif')

        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(CTF_OUTPUT.get_fiber_lengths(), CTF_OUTPUT.fiber_widths, crunched_fibs)
        print(zone_counts, crunched_union_zones[0].area)
        cprint(f"Getting signal density for Zones: [0, 50, 150]", 'yellow')
        for i in range(4):
            cprint(f"{VALUES[i]} signal density: {'{0:.2%}'.format(zone_sums[i] / crunched_union_zones[i].area)}", 'yellow')
    
    # test_basic_crunch_with_fibers()
    # test_basic_crunch_with_new_base_fibers()
    # test_get_fiber_density_and_counts_per_zone_for_every_annotation()
    # test_get_signal_density_only_dcis()
    # test_get_signal_density_crunched_zone()
    # test_get_signal_density_crunched_zone_with_new_base()

#  def test_get_signal_density_only_in_stromal_region_diff_zones():
#         bucketed_fibers = bucket_the_fibers(CTF_OUTPUT.fibers, CTF_OUTPUT.centroids, ANNOTATION_HELPER.annotations)

#         lengths = CTF_OUTPUT.get_fiber_lengths()
#         widths = CTF_OUTPUT.fiber_widths

#         anno_indexes = ANNOTATION_HELPER.get_annotation_indexes() # All
#         final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones([0, 25, 50, 100], anno_indexes)
        
#         singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [1,2,3,4])
#         cprint(f"Singal Density Stromal: {'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')

#         singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [0,1,2,3])
#         cprint(f"Singal Density Stromal: {'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')
        
#         singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, final_union_of_zones, bucketed_fibers, [0,1,2,3,4])
#         cprint(f"Singal Density Stromal: {'{0:.2%}'.format(singnal_dens_only_stromal)}", 'cyan')


    # def test_get_signal_densities_with_controlled_fibers():
    #     fibers_anno1 = du.generate_fibers(15, 125, 175)
    #     bucketed_fibers = bucket_the_fibers(fibers_anno1, CTF_OUTPUT.get_centroids(fibers_anno1), ANNOTATION_HELPER.annotations)
    #     print(bucketed_fibers.shape)
        
    #     anno_indexes = ANNOTATION_HELPER.get_annotation_indexes() # All
    #     final_union_of_zones = ANNOTATION_HELPER.get_final_union_zones([0, 50, 150], anno_indexes)
        
    #     sig_dens, act_counts = get_signal_density_overall(du.get_test_fiber_lengths_from_fibers(fibers_anno1), 
    #                                           du.get_test_fibers_widths(len(fibers_anno1)),
    #                                           final_union_of_zones, bucketed_fibers)
    #     for i in range(4):
    #         cprint(f"{values[i]} signal density: {'{0:.2%}'.format(sig_dens[i])}", 'cyan')
    #         PLOT_HELPER._plot_fibers_per_zone(fibers_anno1, bucketed_fibers, [i])
    #         list_of_union_zones = ANNOTATION_HELPER.get_final_union_zones_for_plotting([0, 50, 150])
    #         PLOT_HELPER._plot_zones(list_of_union_zones)
    #         PLOT_HELPER.show_plot()
    #         PLOT_HELPER.reset()
        


# # Going into bucket_the_fibers at time 2023-04-05 11:45:37.615937
# # Done with bucket_the_fibers in 0.04603886604309082 sec
# # AVERAGE WIDTH
# # DCIS width averages: 5.104434415157757
# # Epithelial width averages: 5.48217150834001
# # Mid-Stromal width averages: 4.780031617139728
# # Other Stromal width averages: 5.936376892030239
# # AVERAGE LENGTHS
# # DCIS length averages: 55.714408846475
# # Epithelial length averages: 65.51393442761696
# # Mid-Stromal length averages: 69.2364216866566
# # Other Stromal length averages: 57.008707779816085
# # AVERAGE Angles
# # DCIS angle averages: 0.4512225724506418
# # Epithelial angle averages: 0.43378574859583996
# # Mid-Stromal angle averages: 0.5389311076343537
# # Other Stromal angle averages: 1.1902899496825317


# # DCIS signal density: 20.62%
# # Epithelial signal density: 20.48%
# # Mid-Stromal signal density: 16.49%
# # Other Stromal signal density: 12.97%

# # Zone 0 signal density: 20.62%
# # Zone 1 signal density: 27.83%
# # Zone 2 signal density: 10.62%
# # Zone 3 signal density: 11.81%
# # Zone 4 signal density: 26.27%


# if gui_tests:
#     pass




# BUCKETING 2:
# DCIS signal density: 7.54%
# Epithelial signal density: 31.29%
# Mid-Stromal signal density: 29.94%
# Other Stromal signal density: 25.23%