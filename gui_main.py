import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import tkinter.messagebox as msg_box
from PIL import ImageTk, Image  
from tkinter import *
import threading
from pathlib import Path
from PIL import Image, ImageTk
import os, sys
import json

from test_export import *
from termcolor import cprint, colored

import sv_ttk
# ('All files', '*.*')


IMG_FILETYPES = (
    ('TIFF files', '*.tif'),
    ('JPEG files', '*.jpg'),
    ('PNG files', '*.png'),
)

GEOJSON_FILETYPES = (
    ('GeoJson files', '*.geojson'),
)

MATLAB_FILETYPES = (
    ('MATLAB files', '*.mat'),  
)

class FileSelector:
    def __init__(self, frame, user_text, row_num, file_types) -> None:
        # Initialize the file selector with a label, entry field, and browse and clear buttons
        self.filetypes = file_types
        self.file_label = tk.Label(frame, text=user_text)
        self.file_label.grid(row=row_num, column=0, padx=5, pady=5)
        self.file_text = tk.StringVar()
        self.file_entry = tk.Entry(frame, textvariable=self.file_text, width=50)
        self.file_entry.grid(row=row_num, column=1, padx=5, pady=5)
        self.file_button = tk.Button(frame, text='Browse', command=self.browse_files)
        self.file_button.grid(row=row_num, column=2, padx=5, pady=5)
        self.file_clear_button = tk.Button(frame, text='Clear', command=self.clear_file)
        self.file_clear_button.grid(row=row_num, column=3, padx=5, pady=5)

    def browse_files(self):
        # Open a file dialog and set the file text if a file is selected
        filename = fd.askopenfilename(title='Open a file', filetypes=self.filetypes)
        if filename:
            self.file_text.set(filename)
        
    def clear_file(self):
        # Clear the file text
        self.file_text.set('')

class MainFrame: 
    def __init__(self, master):
        self.master = master

        # Frames
        self.fileselector_frame = tk.Frame(self.master)
        self.frame = tk.Frame(self.master)
        self.distance_frame = tk.Frame(self.master, bg='green')
        self.display_save_frame = tk.Frame(self.master)
        self.checkbox_frame = tk.Frame(self.master)

        # GUI_HELPER
        self.backend = None
        
        self._initialize_file_selectors()
    
    def _initialize_file_selectors(self):
        # FILE SELECTORS
        self.img_fileselector = FileSelector(self.fileselector_frame, "Upload Image...", 0, IMG_FILETYPES) 
        self.mat_fileselector = FileSelector(self.fileselector_frame, "Upload .mat file...", 1, MATLAB_FILETYPES)     
        self.geojson_fileselector = FileSelector(self.fileselector_frame, "Upload GeoJson...", 2, GEOJSON_FILETYPES)
        
        # Create a button to display the UNEDITED image
        self.display_button = tk.Button(self.fileselector_frame, text='Display Unedited Image', command=self.display_unedited_image)
        self.display_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Create a button to set the GUI_Helper Object
        self.set_up_object_button = tk.Button(self.fileselector_frame, text='Set Up Object', command=self.set_objects)
        self.set_up_object_button.grid(row=4, column=0)
        
        # Create a button to set the GUI_Helper Object
        self.set_up_object_button = tk.Button(self.fileselector_frame, text='Reset Object', command=self.clear_object)
        self.set_up_object_button.grid(row=4, column=1)
        
        #Import Configuration
        self.import_text = tk.StringVar()
        self.import_button = tk.Button(self.fileselector_frame, text='Import Object', command=self.import_info)
        self.import_button.grid(row=4, column=2)
        
        
        # Frames
        self.fileselector_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
        
        self.draw_fibers_colored_by_zone_bool = None
     
    def widgets_to_display_after_obj_set(self):
        #ZONES Entry
        self.csv_boundaries_label = tk.Label(self.frame, text="CSV boundaries of zones (Default: 0, 50, 150):")
        self.csv_boundaries_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")

        self.csv_boundaries_text = tk.StringVar()
        self.csv_boundaries_textbox = tk.Entry(self.frame, textvariable=self.csv_boundaries_text)
        self.csv_boundaries_textbox.grid(row=0, column=1, padx=5, pady=5)

        # Draw Annotations
        self.draw_annotations_var = tk.BooleanVar()
        self.draw_annotations_checkbox = tk.Checkbutton(self.frame, text="Draw Annotations", variable=self.draw_annotations_var)
        self.draw_annotations_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="W")

        self.draw_annotations_info_var = tk.BooleanVar()
        self.draw_annotations_info_checkbox = tk.Checkbutton(self.frame, text="Draw Annotation Info", variable=self.draw_annotations_info_var)
        self.draw_annotations_info_checkbox.grid(row=1, column=3, padx=5, pady=5, sticky="W")
        
        self.draw_annotations_textbox = tk.Entry(self.frame)
        self.draw_annotations_textbox.grid(row=1, column=1, padx=5, pady=5)
        self.draw_annotations_label = tk.Label(self.frame, text="- CSV Annotations to draw. Names/Indexes (Default: All)")
        self.draw_annotations_label.grid(row=1, column=2, padx=5, pady=5, sticky="W")

        # Draw Fibers
        self.draw_fibers_var = tk.BooleanVar()
        self.draw_fibers_checkbox = tk.Checkbutton(self.frame, text="Draw Fibers", variable=self.draw_fibers_var)
        self.draw_fibers_checkbox.grid(row=2, column=0, padx=5, pady=5, sticky="W")

        # Draw Zones
        self.draw_zones_var = tk.BooleanVar()
        self.draw_zones_checkbox = tk.Checkbutton(self.frame, text="Draw Zones", variable=self.draw_zones_var)
        self.draw_zones_checkbox.grid(row=3, column=0, padx=5, pady=5, sticky="W")
        
        self.draw_zones_textbox = tk.Entry(self.frame)
        self.draw_zones_textbox.grid(row=3, column=1, padx=5, pady=5)
        
        self.draw_zones_label = tk.Label(self.frame, text="- CSV Zones to draw. Integers - (Default: All)")
        self.draw_zones_label.grid(row=3, column=2, padx=5, pady=5, sticky="W")

        self.draw_zones_opacity_text = tk.StringVar()
        self.draw_zones_opacity_textbox = tk.Entry(self.frame, textvariable=self.draw_zones_opacity_text, width=10)
        self.draw_zones_opacity_textbox.grid(row=3, column=3, padx=5, pady=5, sticky="W")
        
        self.draw_zones_opacity_label = tk.Label(self.frame, text="Opacity (0-256)")
        self.draw_zones_opacity_label.grid(row=3, column=3, padx=5, pady=5, sticky="E")
        
        # Crunch Settings
        self.crunch_annotations_bool = tk.BooleanVar()
        self.crunch_annotations_checkbox = tk.Checkbutton(self.frame, text="Crunch Annotations", variable=self.crunch_annotations_bool,
                                                          command=self.toggle_crunch)
        self.crunch_annotations_checkbox.grid(row=4, column=0, padx=5, pady=5, sticky="W")

        self.crunch_base_text = tk.StringVar()
        self.crunch_base_textbox = tk.Entry(self.frame, textvariable=self.crunch_base_text)
        self.crunch_base_textbox.grid(row=4, column=1, padx=5, pady=5, sticky="W")

        self.crunch_base_description_label = tk.Label(self.frame, text="- CSV Annotations to crunch on. Names/Indexes (Default: All)")
        self.crunch_base_description_label.grid(row=4, column=2, padx=5, pady=5, sticky="W")
        
        self.crunch_ignore_text = tk.StringVar()
        self.crunch_ignore_textbox = tk.Entry(self.frame, textvariable=self.crunch_ignore_text, width=10)
        self.crunch_ignore_textbox.grid(row=4, column=3, padx=5, pady=5, sticky="W")
        self.crunch_ignore_text.set('0,1')
        
        self.crunch_ignore_label = tk.Label(self.frame, text=" Zones Ignored")
        self.crunch_ignore_label.grid(row=4, column=3, padx=5, pady=5, sticky="E")
        
        self.crunch_base_textbox.config(state='disabled')
        self.crunch_ignore_textbox.config(state='disabled')
        
        # Fiber Distances
        self.distance_fibers_button = tk.Button(self.frame, bg='green', text='Get Fiber Distances', command=self.get_fiber_distances)
        self.distance_fibers_button.grid(row=5, column=0, padx=5, pady=5, sticky="W")

        self.distance_fibers_text = tk.StringVar()
        self.distance_fibers_textbox = tk.Entry(self.frame, textvariable=self.distance_fibers_text)
        self.distance_fibers_textbox.grid(row=5, column=1, padx=5, pady=5, sticky="W")

        self.distance_fibers_description_label = tk.Label(self.frame, text="- CSV Annotations to get distances on. Names/Indexes (Default: All)")
        self.distance_fibers_description_label.grid(row=5, column=2, padx=5, pady=5, sticky="W")

        self.distance_fibers_label = tk.Label(self.frame, text="Fibers currently UNDISTANCED!", fg= "red")
        self.distance_fibers_label.grid(row=6,padx=5, pady=5, sticky="W")
        
        # Display Edited Image Button
        self.display_edited_image_button = tk.Button(self.display_save_frame, bg='cyan', text='Display Edited Image', command=self.display_image)
        self.display_edited_image_button.grid(row=0, padx=5, pady=5, sticky="W")
        
        # Save Image Button
        self.save_button = tk.Button(self.display_save_frame, text='Save Image', bg='lime', command=self.save_image)
        self.save_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.save_image_textbox = tk.Entry(self.display_save_frame, width=60)
        self.save_image_textbox.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="W")
        
        self.frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
        self.display_save_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
    
    def widgets_to_display_after_distancing(self):
        self.draw_fibers_label = tk.Label(self.distance_frame, text="CSV of Zones of Fibers to draw (Default: All): ")
        self.draw_fibers_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
        
        self.draw_fibers_textbox = tk.Entry(self.distance_frame)
        self.draw_fibers_textbox.grid(row=0, column=1, padx=5, pady=5)
        
        self.draw_fibers_colored_by_zone_bool = tk.BooleanVar()
        self.draw_fibers_colored_by_zone_checkbox = tk.Checkbutton(self.distance_frame,
                                                                   text="Draw Fibers Same Color as Zones",
                                                                   variable=self.draw_fibers_colored_by_zone_bool)
        self.draw_fibers_colored_by_zone_checkbox.grid(row=0, column=2, padx=5, pady=5, sticky="W")
        
        self.get_averages_button = tk.Button(self.distance_frame, text='Calculate Averages', command=self.display_averages)
        self.get_averages_button.grid(row=2, padx=5, pady=5, sticky="W")
        
        # Calculate the Signal Densities Button:
        self.get_signal_densities_button = tk.Button(self.distance_frame, text='Calculate Signal Densities', command=self.display_signal_densities)
        self.get_signal_densities_button.grid(row=3, padx=5, pady=5, sticky="W")
        
        # Calculate the Combination:
        self.get_combo_signal_densities_button = tk.Button(self.distance_frame, text='Calculate Combination Signal Densities', command=self.display_combination_signal_densities)
        self.get_combo_signal_densities_button.grid(row=4, padx=5, pady=5, sticky="W")
        
        self.get_combo_signal_densities_textbox = tk.Entry(self.distance_frame)
        self.get_combo_signal_densities_textbox.grid(row=4, column=1, padx=5, pady=5)
        
        self.get_combo_signal_densities_label = tk.Label(self.distance_frame, text="- CSV values for zones to combine (Default: All)")
        self.get_combo_signal_densities_label.grid(row=4, column=2, padx=5, pady=5, sticky="W")
        
        # Calculate the Combination:
        self.get_sig_dens_per_anno_button = tk.Button(self.distance_frame, text='Calculate Signal Densities Per Anno', command=self.display_sig_dens_per_anno)
        self.get_sig_dens_per_anno_button.grid(row=5, padx=5, pady=5, sticky="W")
        
        # Export all information:
        self.export_info_button = tk.Button(self.distance_frame, text='Export all information', command=self.export_info)
        self.export_info_button.grid(row=6, padx=5, pady=5, sticky="W")
        
        self.export_info_text = tk.StringVar()
        self.export_info_textbox = tk.Entry(self.distance_frame, textvariable=self.export_info_text, width=60)
        self.export_info_textbox.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky="W")
        
        self.export_compressed_bool = tk.BooleanVar()
        self.export_compressed_checkbox = tk.Checkbutton(
            self.distance_frame,
            text="Compress Numpy Distance Arr",
            variable=self.export_compressed_bool
        )
        self.export_compressed_checkbox.grid(row=6, column=3, padx=5, pady=5, sticky="W")
        
        # PACK IT
        self.distance_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
    
    def set_objects(self):
        # Do quick clear!
        self.backend = None
        self.frame.pack_forget()
        self.display_save_frame.pack_forget()
        self.distance_frame.pack_forget()
        
        mat_file = self.mat_fileselector.file_text.get()
        img_file = self.img_fileselector.file_text.get()
        anno_file = self.geojson_fileselector.file_text.get()
         
        if img_file == '' or mat_file == '' or anno_file == '':
            cprint("All files must be set! Object not set!", "red")
            msg_box.showerror("Set Objects Error", "All files must be set! Object not set!")
            return 
        
        self.backend = GUI_Helper(img_file, mat_file, anno_file)
        self.widgets_to_display_after_obj_set()
        cprint("All objects set!", "cyan")

    def clear_object(self):
        self.img_fileselector.clear_file()
        self.mat_fileselector.clear_file()
        self.geojson_fileselector.clear_file()
        self.backend = None
        self.frame.pack_forget()
        self.display_save_frame.pack_forget()
        self.distance_frame.pack_forget()
        self.draw_fibers_colored_by_zone_bool = None
        cprint("Clearing the object!", 'cyan')

    def get_zone_boundaries(self):
        zone_boundaries = [0, 50, 150]
        if(self.csv_boundaries_text.get()):
            zone_boundaries = self.split_string_to_ints(self.csv_boundaries_text.get())
        return zone_boundaries
    
    def toggle_crunch(self):
        if self.crunch_annotations_bool.get():
            self.crunch_base_textbox.config(state='normal')
            self.crunch_ignore_textbox.config(state='normal')
        else:
            self.crunch_base_textbox.config(state='disabled')
            self.crunch_ignore_textbox.config(state='disabled')
            
    def finalize_image(self):
        self.backend.DRAW_HELPER.reset()
    
        if(self.draw_annotations_var.get()):
            if self.draw_annotations_textbox.get():
                values_to_draw = [x.strip() for x in self.draw_annotations_textbox.get().split(',')]
                anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(values_to_draw)
                self.backend.DRAW_HELPER.draw_annotations(
                    self.backend.ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes),
                    draw_anno_indexes=self.draw_annotations_info_var.get())
            else:
                self.backend.DRAW_HELPER.draw_annotations(self.backend.ANNOTATION_HELPER.annotations,
                                                          draw_anno_indexes=self.draw_annotations_info_var.get())

        base_annotations_to_draw = []
        if self.distance_fibers_text.get():
            base_annotations_to_draw = [x.strip() for x in self.distance_fibers_text.get().split(',')]
        base_anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(base_annotations_to_draw)

        # NOTE: Add feature to draw_fibers of specific colors per zone if dist_fibers
        if(self.draw_fibers_var.get()):
            verts = self.backend.CTF_OUTPUT.fibers
            widths = self.backend.CTF_OUTPUT.fiber_widths
            if(self.backend.fiber_dists is not None and self.draw_fibers_textbox.get()):
                fiber_zones = self.split_string_to_ints(self.draw_fibers_textbox.get())
                zone_boundaries = self.get_zone_boundaries()
                if(self.crunch_annotations_bool.get()):
                    annotations_to_crunch_on = []
                    if self.crunch_base_text.get():
                        annotations_to_crunch_on = [x.strip() for x in self.crunch_base_text.get().split(',')]
                    crunch_anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_crunch_on)
                    ignore_zones = self.split_string_to_ints(self.crunch_ignore_text.get())

                    crunched_fibs = get_crunched_fibers(self.backend.fiber_dists, crunch_anno_indexes, base_anno_indexes,
                                                        buckets=zone_boundaries, to_ignore=ignore_zones)
                    self.backend.DRAW_HELPER.draw_fibers_per_zone(verts, widths, crunched_fibs, fiber_zones,self.draw_fibers_colored_by_zone_bool.get())
                else:
                    bucketed_fibers = self.backend.get_bucket_for_each_fiber(base_anno_indexes, zone_boundaries)
                    self.backend.DRAW_HELPER.draw_fibers_per_zone(verts, widths, bucketed_fibers, fiber_zones,self.draw_fibers_colored_by_zone_bool.get())
            else:
                if(self.draw_fibers_colored_by_zone_bool and self.draw_fibers_colored_by_zone_bool.get()):
                    self.backend.DRAW_HELPER.draw_fibers_colored_per_zone(verts, widths, self.backend.current_fibers)
                else:
                    self.backend.DRAW_HELPER.draw_fibers(verts, widths)
                
        if(self.draw_zones_var.get()):
            zone_boundaries = self.get_zone_boundaries()            
            del_zones = None
            # Getting Normal Zones or Crunched Zones
            if(self.crunch_annotations_bool.get()):
                annotations_to_crunch_on = []
                if self.crunch_base_text.get():
                    annotations_to_crunch_on = [x.strip() for x in self.crunch_base_text.get().split(',')]
                crunch_anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_crunch_on)
                ignore_zones = self.split_string_to_ints(self.crunch_ignore_text.get())
                zones, del_zones = self.backend.ANNOTATION_HELPER.get_zones_crunched(zone_boundaries, crunch_anno_indexes, base_anno_indexes, ignore_zones)
            else:
                zones = self.backend.ANNOTATION_HELPER.get_final_union_zones(zone_boundaries, base_anno_indexes)

            opacity = self.draw_zones_opacity_textbox.get()
            if opacity:
                try:
                    opacity = int(opacity)
                    if(opacity > 256 or opacity < 0):
                        opacity = max(min(opacity, 256), 0)
                        cprint(f"Opacity {opacity} Not In Correct Range", 'red')
                except ValueError:
                    opacity = ''
                    cprint("Opacity Has to be a number from 0-256. Setting to 32", 'red')
                    msg_box.showerror("Opacity Error", "Opacity Has to be a number from 0-256")
            
            if opacity == '':
                opacity = 32
            
            self.draw_zones_opacity_text.set(str(opacity))
    
            to_draw = list(np.arange(len(zones)))
            if(self.draw_zones_textbox.get()):
                to_draw = self.split_string_to_ints(self.draw_zones_textbox.get())
            # self.backend.DRAW_HELPER.draw_zone_outlines(zones, to_draw=to_draw) #  to_draw=[1, 3]
            self.backend.DRAW_HELPER.draw_zones(zones, del_zones, to_draw=to_draw, opacity=opacity) #  to_draw=[1, 3]

    def display_image(self):
        filename = self.img_fileselector.file_text.get()
        if(self.backend):
            self.finalize_image()
            self.newWindow = tk.Toplevel(self.master)
            self.app = ImageWindow(self.newWindow, image=self.backend.DRAW_HELPER.get_image(), backend=self.backend)
        elif filename:
            self.newWindow = tk.Toplevel(self.master)
            self.app = ImageWindow(self.newWindow, filename)
    
    def display_unedited_image(self):
        filename = self.img_fileselector.file_text.get()
        if filename:
            self.newWindow = tk.Toplevel(self.master)
            self.app = ImageWindow(self.newWindow, filename)

    def save_image(self):
        filename = fd.asksaveasfilename(defaultextension=".tif",
                                                filetypes=IMG_FILETYPES)
        if filename:
            self.finalize_image()
            self.backend.DRAW_HELPER.save_file_overlay(filename)
            self.save_image_textbox.delete(0, tk.END)
            self.save_image_textbox.insert(0, filename)

    def get_fiber_distances(self):
        """Note: This function is threaded because the distancing is not the fastest thing in the west"""
        if(self.backend):
            if(self.csv_boundaries_textbox.get()):
                zone_boundaries = self.split_string_to_ints(self.csv_boundaries_textbox.get())
                if zone_boundaries is None:
                    return

                if(0 not in zone_boundaries):
                    err_msg = f"Zero is required as first value for zones!"
                    msg_box.showerror("Zone Value Error", err_msg)
                    cprint(f"{err_msg}", 'red')
                    self.csv_boundaries_text.set("")
                    return
            else:
                zone_boundaries = [0, 50, 150]
            
            self.distance_fibers_label.config(text='Currently Distancing the Fibers...', fg= "orange")
            fibers = self.backend.CTF_OUTPUT.fibers
            centroids = self.backend.CTF_OUTPUT.centroids
            
            annotations_to_draw = []
            if self.distance_fibers_text.get():
                annotations_to_draw = [x.strip() for x in self.distance_fibers_text.get().split(',')]
            anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_draw)

            self.backend.reset()
            
            def distance_fibers():
                self.backend.get_all_fiber_dists_for_each_anno(fibers, centroids, self.backend.ANNOTATION_HELPER.annotations)
                self.backend.annotations_indexes_distanced_on = anno_indexes 
                self.distance_fibers_label.config(text='Fibers are currently Distanced!', fg= "green")
                self.widgets_to_display_after_distancing()
                
                if(self.crunch_annotations_bool.get()):
                    annotations_to_crunch_on = []
                    if self.crunch_base_text.get():
                        annotations_to_crunch_on = [x.strip() for x in self.crunch_base_text.get().split(',')]
                    crunch_anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_crunch_on)
                    ignore_zones = self.split_string_to_ints(self.crunch_ignore_text.get())
                    
                    self.backend.current_fibers = get_crunched_fibers(self.backend.fiber_dists, crunch_anno_indexes,
                                                                      anno_indexes, buckets=zone_boundaries,
                                                                      to_ignore=ignore_zones)
                    self.backend.list_of_zones, del_zones = self.backend.ANNOTATION_HELPER.get_zones_crunched(
                        zone_boundaries, crunch_anno_indexes, anno_indexes, zones_to_ignore=ignore_zones
                    )
                    self.backend.delete_zones = del_zones
                else:
                    self.backend.current_fibers = self.backend.get_bucket_for_each_fiber(anno_indexes, zone_boundaries)
                    self.backend.list_of_zones = self.backend.ANNOTATION_HELPER.get_final_union_zones(zone_boundaries, anno_indexes)
                    self.backend.delete_zones = None
                    
            threading.Thread(target=distance_fibers).start() 

    def display_averages(self):
        width_avgs, len_avgs, ang_avgs= self.calc_averages()
        zone_bound_len = len(self.get_zone_boundaries()) + 1
        
        width_avg_str = "Width Averages: \n"
        for i in range(zone_bound_len):
            width_avg_str+=f"\t Zone {i} width averages: {width_avgs[i]}\n"
        width_avg_str+=f"\t Total Average Width {np.mean(width_avgs[-1])}\n"
        msg_box.showinfo("Width Info", width_avg_str)
        width_avg_str+=f"\t List Form: {list(width_avgs.values())}\n"
        
        len_avg_str = "Length Averages: \n"
        for i in range(zone_bound_len):
            len_avg_str+=f"\t Zone {i} length averages: {len_avgs[i]}\n"
        len_avg_str+=f"\t Total Average Length {np.mean(len_avgs[-1])}\n"
        msg_box.showinfo("Length Info", len_avg_str)
        len_avg_str+=f"\t List Form: {list(len_avgs.values())}\n"
        
        ang_avg_str = "Angle Averages: \n"
        for i in range(zone_bound_len):
            ang_avg_str+=f"\t Zone {i} angle averages: {ang_avgs[i]}\n"
        ang_avg_str+=f"\t Total Average Angle {np.mean(ang_avgs[-1])}\n"
        msg_box.showinfo("Angle Info", ang_avg_str)
        ang_avg_str+=f"\t List Form: {list(ang_avgs.values())}\n"
        
        cprint(width_avg_str, 'yellow')
        cprint(len_avg_str, 'cyan')
        cprint(ang_avg_str, 'magenta')
    
    def calc_averages(self):
        zone_bound_len = len(self.get_zone_boundaries()) + 1
        
        widths = self.backend.CTF_OUTPUT.fiber_widths
        width_avgs = get_average_value_per_zone(widths, self.backend.current_fibers, zone_bound_len)
        width_avgs[-1] = np.mean(widths)
        
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths()
        len_avgs = get_average_value_per_zone(lengths, self.backend.current_fibers, zone_bound_len)
        len_avgs[-1] = np.mean(lengths)
        
        angles = self.backend.CTF_OUTPUT.fiber_angles
        ang_avgs = get_average_value_per_zone(angles, self.backend.current_fibers, zone_bound_len)
        ang_avgs[-1] = np.mean(angles)
        
        return width_avgs, len_avgs, ang_avgs

    def display_signal_densities(self):
        zone_boundaries = self.get_zone_boundaries()
        sig_dens, act_counts, zone_sums = self.calc_signal_densities()
        sig_dens_str = "\nSignal Densities:"
        for i, dens in enumerate(sig_dens):
            sig_dens_str+= f"\n\tZone {i}: signal density: {'{0:.2%}'.format(dens)}"
            
        # for i in range(len(zone_boundaries) + 1):
        #     sig_dens_str+= f"\n\tZone {i}: signal density: {'{0:.2%}'.format(sig_dens[i])}"
        msg_box.showinfo("Signal Density Info", sig_dens_str)
        sig_dens_str+=f"\n\tList Form: {sig_dens}"
        sig_dens_str+=f"\n\tCounts per Zone: {act_counts}"
        sig_dens_str+=f"\n\tSums per Zone: {zone_sums}\n"
        cprint(sig_dens_str, 'cyan')

    def calc_signal_densities(self):
        cprint("Calculating Signal Density", 'cyan')
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths()
        widths = self.backend.CTF_OUTPUT.fiber_widths
        
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(lengths, widths, self.backend.current_fibers)
        areas = []
        sig_dens = []
        for i, list_zone in enumerate(self.backend.list_of_zones):
            print(i, list_zone.area)
            sig_dens.append(zone_sums[i]/list_zone.area)
            areas.append(list_zone.area)
        if(self.backend.delete_zones):
            print("Yes delete zones", self.backend.delete_zones.area)
            sig_dens.append(zone_sums[-1]/self.backend.delete_zones.area)
            areas.append(self.backend.delete_zones.area)
        print(areas, sum(areas))
        return sig_dens, zone_counts, zone_sums
    
    def display_combination_signal_densities(self):
        singnal_dens_only_stromal, zones_to_combo = self.calc_combination_signal_densities()
        
        combo_sig_dens_str = "\nSignal Densities:"
        combo_sig_dens_str+= f"\n\tZone {zones_to_combo}: signal density: {'{0:.2%}'.format(singnal_dens_only_stromal)}"
        msg_box.showinfo("Signla Density Info", combo_sig_dens_str)
        cprint(combo_sig_dens_str, 'cyan')

    def calc_combination_signal_densities(self):
        cprint("Calculating Combination Signal Density", 'cyan')
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths()
        widths = self.backend.CTF_OUTPUT.fiber_widths
        
        zones_to_combo = list(range(len(self.backend.list_of_zones)))
        if(self.get_combo_signal_densities_textbox.get()):
            zones_to_combo =  self.split_string_to_ints(self.get_combo_signal_densities_textbox.get())
        zone_sums, zone_counts = get_fiber_density_and_counts_per_zone(lengths, widths, self.backend.current_fibers)
        singnal_dens_only_stromal = get_signal_density_per_desired_zones(zone_sums, self.backend.list_of_zones, zones_to_combo)
        self.backend.combo_zones_numbers[str(zones_to_combo)] = singnal_dens_only_stromal
        return singnal_dens_only_stromal, zones_to_combo
          
    def split_string_to_ints(self, textbox_value):
        try:
            to_ret = [] 
            for x in textbox_value.split(','):
                if(x.strip()):
                    to_ret.append(int(x.strip()))
            return list(sorted(to_ret))
        except ValueError as e:
            err_msg = f"Could not split value from textbox with value: {textbox_value}"
            msg_box.showerror("Split Value Error", err_msg)
            cprint(f"{err_msg} - {e}", 'red')
            return None

    def display_sig_dens_per_anno(self):
        sig_dens_per_anno = self.calc_sig_dens_per_anno()
        combo_sig_dens_str = "\nSignal Densities Per Annotation:"
        combo_sig_dens_str+= f"\n\t{sig_dens_per_anno}"
        msg_box.showinfo("Signla Density Info", combo_sig_dens_str)
        cprint(combo_sig_dens_str, 'cyan')
        
    def calc_sig_dens_per_anno(self):
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths()
        widths = self.backend.CTF_OUTPUT.fiber_widths
        # annotations_to_draw = []
        # if self.distance_fibers_text.get():
        #     annotations_to_draw = [x.strip() for x in self.distance_fibers_text.get().split(',')]
        # annotations_to_use = self.backend.ANNOTATION_HELPER.get_annotations_from_indexes(annotations_to_draw)
        return get_signal_density_for_all_annotations(self.backend.fiber_dists, 
                                                      self.backend.ANNOTATION_HELPER.annotations, lengths, widths)
    
    def export_info(self):
        filename = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("text", "*.txt")])
        if filename:
            print(f"Exporting Information to {filename}...")
            
            self.export_info_text.set(filename)    
            np.savetxt(filename, self.backend.fiber_dists, delimiter='\t')
    
            if(self.export_compressed_bool.get()):
                self.export_info_text.set(filename)    
                np.save(f"{os.path.splitext(filename)[0]}.npy", self.backend.fiber_dists)
                    
            width_avgs, len_avgs, ang_avgs = self.calc_averages()
            sig_dens, act_counts, zone_sums = self.calc_signal_densities()
            act_counts = [int(x) for x in act_counts]
            zone_sums = [int(x) for x in zone_sums]

            if(self.distance_fibers_text.get()):
                annotations_selected = self.distance_fibers_text.get()
            else:
                annotations_selected = 'ALL'
            
            annotations_to_crunch_on = []
            if self.crunch_base_text.get():
                annotations_to_crunch_on = [x.strip() for x in self.crunch_base_text.get().split(',')]
            crunch_anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_crunch_on)
            
            zone_areas = []
            for zone in self.backend.list_of_zones:
                zone_areas.append(zone.area)

            test_dict = {
                'Averages': {
                    'Widths': list(width_avgs.values()),
                    'Lengths': list(len_avgs.values()),
                    'Angles': list(ang_avgs.values()),
                },
                'Crunched': self.crunch_annotations_bool.get(),
                'Annotations Crunched On': self.crunch_base_text.get(),
                'Annotations Indexes Crunched On': crunch_anno_indexes,
                'Zones Ignored for Crunching': self.crunch_ignore_text.get(),
                'Annotations Bucketed On': annotations_selected,
                'Annotation Indexes Bucketed On': self.backend.annotations_indexes_distanced_on,
                'Signal Densities per Annotation': list(self.calc_sig_dens_per_anno()),
                'Signal Densities': sig_dens,
                'Zone Sums': zone_sums,
                'Zone Areas': zone_areas,
                'Actual Counts': act_counts,
                'Zones': self.get_zone_boundaries(),
                'Combination Signal Densities': self.backend.combo_zones_numbers,
                'GeoJson File': self.geojson_fileselector.file_text.get(),
                'Mat File': self.mat_fileselector.file_text.get(),
                'Img File': self.img_fileselector.file_text.get()
            }

            with open(f"{os.path.splitext(filename)[0]}.json", 'w') as fp:
                json.dump(test_dict, fp, sort_keys=True, indent=2)
            
            self.save_as_tsv(test_dict, filename) 
    
    def save_as_tsv(self, json_dict, filename):
        tsv_data = ""

        for key, value in json_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if(isinstance(sub_value, list)):
                        tsv_data += f"{key}\t{sub_key}\t" + "\t".join(map(str, sub_value)) + "\n"
                    else:
                        tsv_data += f"{key}\t{sub_key}\t{sub_value}\n"
            else:
                if(isinstance(value, list)):
                    tsv_data += f"{key}\t" + "\t".join(map(str, value)) + "\n"
                else:
                    # print(f"{key}\t{value}")
                    tsv_data += f"{key}\t{value}\n"
        tsv_data+='\n'
        with open(f"{os.path.splitext(filename)[0]}.tsv", 'w') as file:
            file.write(tsv_data)
    
    def display_as_array_to_copy(self, dict):
        return str(list(dict.values())).replace(',',  '\t')
    
    def import_info(self):
        cprint("Importing the info!", 'magenta')
        filename = fd.askopenfilename(title='Open a file', filetypes=[('JSON files', '*.json')])
        if filename:
            self.import_text.set(filename)
            with open(filename) as fp:
                data = json.load(fp)
            if('Img File' in data):
                self.clear_object()
                self.mat_fileselector.file_text.set(data['Mat File']) 
                self.img_fileselector.file_text.set(data['Img File'])
                self.geojson_fileselector.file_text.set(data['GeoJson File']) 
                
                self.backend = GUI_Helper(data['Img File'], data['Mat File'], data['GeoJson File'])
                self.widgets_to_display_after_obj_set()
                cprint("All objects set!", "cyan")
                
                if('Zones' in data):
                        self.csv_boundaries_text.set(str(data['Zones'])[1:-1])
                    
                if('Annotations Bucketed On' in data):
                    anno_info = data['Annotations Bucketed On']
                    if(anno_info != 'ALL'):
                        self.distance_fibers_text.set(anno_info)
                        
                self.crunch_annotations_bool.set(data['Crunched'])
                if('Annotations Crunched On' in data):
                    self.crunch_base_text.set(data['Annotations Crunched On'])
                    
                if('Zones Ignored for Crunching' in data):
                    self.crunch_ignore_text.set(data['Zones Ignored for Crunching']) 
                    
            
                if os.path.isfile(f"{os.path.splitext(filename)[0]}.npy"):
                    self.backend.fiber_dists = np.load(f"{os.path.splitext(filename)[0]}.npy")
                    self.distance_fibers_label.config(text='Fibers currently DISTANCED!', fg= "green")
                    self.widgets_to_display_after_distancing()
                    
                cprint("Distanced Fibers Loaded", "cyan")
            
            else:
                cprint("Not a valid json file to set object!", "red")
                
class ImageWindow:
    def __init__(self, master, filename=None, image=None, backend=None):
        self.master = master
        self.frame = Frame(self.master)
        if(filename):
            self.image = Image.open(filename)
        else:
            self.image = image
        self.img_copy = self.image.copy()

        self.original_size_x = self.img_copy.size[0]
        self.original_size_y = self.img_copy.size[1]
         
        x_img = self.img_copy.size[0]
        y_img = self.img_copy.size[1]
        if(x_img > 800):
            x_img = 800
        
        if(y_img > 800):
            y_img = 800
            
        self.image = self.img_copy.resize((x_img, y_img))

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = Label(self.master, image=self.background_image, borderwidth=0, highlightthickness=0)
        self.background.pack(fill=BOTH, expand=YES)
        self.background.pack(side="top", fill="both", expand=True)

        self.background.bind('<Configure>', self._resize_image)
        self.background.bind('<Button 1>', self.getorigin)
        
        self.gui_helper = backend
        
    def _resize_image(self,event):
        new_width = event.width
        new_height = event.height

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image =  self.background_image)

    def getorigin(self, eventorigin):
      global x,y
      x = eventorigin.x
      y = eventorigin.y
      
      corrected_x = x * self.original_size_x /  self.image.size[0]
      corrected_y = y * self.original_size_y /  self.image.size[1]
      if(self.gui_helper):
            corrected_point = geo.Point(corrected_x, corrected_y)
            lengths = self.gui_helper.CTF_OUTPUT.get_fiber_lengths()
            widths = self.gui_helper.CTF_OUTPUT.fiber_widths
            for anno in self.gui_helper.ANNOTATION_HELPER.annotations:
                if(anno.geo_polygon.contains(corrected_point)):
                    if(self.gui_helper.fiber_dists is not None):
                        signal_dens = get_signal_density_per_annotation(
                            self.gui_helper.fiber_dists[:, anno.original_index],
                            self.gui_helper.ANNOTATION_HELPER.annotations[anno.original_index],
                            lengths, widths
                        )
                        print(f"{corrected_point} - {anno} \nSignal Density: {signal_dens}\n")
                    else:
                        print(f"{corrected_point} - {anno}\n")
                           

def main(): 
    root = Tk()
    root.title("DCIS Helper")
    root.geometry("1000x750")

    # sv_ttk.set_theme("dark")
    
    menu_window = MainFrame(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()



