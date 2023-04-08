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
        filename = fd.askopenfilename(title='Open a file', filetypes=self.filetypes)
        if filename:
            self.file_text.set(filename)
        
    def clear_file(self):
        self.file_text.set('')

class MainFrame: 
    def __init__(self, master):
        self.master = master

        # Frames
        self.fileselector_frame = tk.Frame(self.master)
        self.frame = tk.Frame(self.master)
        self.bucketed_frame = tk.Frame(self.master, bg='green')
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
        self.set_up_object_button = tk.Button(self.fileselector_frame, text='Set Up Objects', command=self.set_objects)
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
        self.draw_annotations_label = tk.Label(self.frame, text="- CSV Annotations Names to draw (Default: All)")
        self.draw_annotations_label.grid(row=1, column=2, padx=5, pady=5, sticky="W")

        # Draw Fibers
        self.draw_fibers_var = tk.BooleanVar()
        self.draw_fibers_checkbox = tk.Checkbutton(self.frame, text="Draw Fibers", variable=self.draw_fibers_var)
        self.draw_fibers_checkbox.grid(row=2, column=0, padx=5, pady=5, sticky="W")

        # Bucket Fibers Bucket
        self.bucket_fibers_button = tk.Button(self.frame, bg='green', text='Bucket the Fibers', command=self.bucket_the_fibers)
        self.bucket_fibers_button.grid(row=4, column=0, padx=5, pady=5, sticky="W")

        self.bucket_fibers_text = tk.StringVar()
        self.bucket_fibers_textbox = tk.Entry(self.frame, textvariable=self.bucket_fibers_text)
        self.bucket_fibers_textbox.grid(row=4, column=1, padx=5, pady=5, sticky="W")

        self.bucket_fibers_description_label = tk.Label(self.frame, text="- CSV Annotations Names to bucket on (Default: All)")
        self.bucket_fibers_description_label.grid(row=4, column=2, padx=5, pady=5, sticky="W")
        
        self.bucket_fibers_label = tk.Label(self.frame, text="Fibers currently UNBUCKETED!", fg= "red")
        self.bucket_fibers_label.grid(row=5,padx=5, pady=5, sticky="W")
        
        # self.bucket_indexes_text = tk.StringVar()
        # self.bucket_indexes_textbox = tk.Entry(self.frame, textvariable=self.bucket_indexes_text)
        # self.bucket_indexes_textbox.grid(row=5, column=1, padx=5, pady=5, sticky="W")

        # self.bucket_indexes_description_label = tk.Label(self.frame, text="- CSV Indexes to bucket on (Default: None)")
        # self.bucket_indexes_description_label.grid(row=5, column=2, padx=5, pady=5, sticky="W")
        
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
    
    def widgets_to_display_after_bucketing(self):
        self.draw_fibers_label = tk.Label(self.bucketed_frame, text="CSV of Zones of Fibers to draw (Default: All): ")
        self.draw_fibers_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
        
        self.draw_fibers_textbox = tk.Entry(self.bucketed_frame)
        self.draw_fibers_textbox.grid(row=0, column=1, padx=5, pady=5)

        # Draw Zones
        self.draw_zones_var = tk.BooleanVar()
        self.draw_zones_checkbox = tk.Checkbutton(self.bucketed_frame, text="Draw Zones", variable=self.draw_zones_var)
        self.draw_zones_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="W")
        
        self.draw_zones_textbox = tk.Entry(self.bucketed_frame)
        self.draw_zones_textbox.grid(row=1, column=1, padx=5, pady=5)
        
        self.draw_zones_label = tk.Label(self.bucketed_frame, text="- CSV values for zones to draw (Default: All)")
        self.draw_zones_label.grid(row=1, column=2, padx=5, pady=5, sticky="W")

        # Calculate the averages button:
        self.get_averages_button = tk.Button(self.bucketed_frame, text='Calculate Averages', command=self.display_averages)
        self.get_averages_button.grid(row=2, padx=5, pady=5, sticky="W")
        
        # Calculate the Signal Densities Button:
        self.get_signal_densities_button = tk.Button(self.bucketed_frame, text='Calculate Signal Densities', command=self.display_signal_densities)
        self.get_signal_densities_button.grid(row=3, padx=5, pady=5, sticky="W")
        
        # Calculate the Combination:
        self.get_combo_signal_densities_button = tk.Button(self.bucketed_frame, text='Calculate Combination Signal Densities', command=self.display_combination_signal_densities)
        self.get_combo_signal_densities_button.grid(row=4, padx=5, pady=5, sticky="W")
        
        self.get_combo_signal_densities_textbox = tk.Entry(self.bucketed_frame)
        self.get_combo_signal_densities_textbox.grid(row=4, column=1, padx=5, pady=5)
        
        self.get_combo_signal_densities_label = tk.Label(self.bucketed_frame, text="- CSV values for zones to combine (Default: All)")
        self.get_combo_signal_densities_label.grid(row=4, column=2, padx=5, pady=5, sticky="W")
        
        # Calculate the Combination:
        self.get_sig_dens_per_anno_button = tk.Button(self.bucketed_frame, text='Calculate Signal Densities Per Anno', command=self.display_sig_dens_per_anno)
        self.get_sig_dens_per_anno_button.grid(row=5, padx=5, pady=5, sticky="W")
        
        # Export all information:
        self.export_info_button = tk.Button(self.bucketed_frame, text='Export all information', command=self.export_info)
        self.export_info_button.grid(row=6, padx=5, pady=5, sticky="W")
        
        self.export_info_text = tk.StringVar()
        self.export_info_textbox = tk.Entry(self.bucketed_frame, textvariable=self.export_info_text, width=60)
        self.export_info_textbox.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky="W")
        
        self.export_compressed_bool = tk.BooleanVar()
        self.export_compressed_checkbox = tk.Checkbutton(
            self.bucketed_frame,
            text="Compress Numpy Bucket Arr",
            variable=self.export_compressed_bool
        )
        self.export_compressed_checkbox.grid(row=6, column=3, padx=5, pady=5, sticky="W")
        
        # PACK IT
        self.bucketed_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
    
    def set_objects(self):
        mat_file = self.mat_fileselector.file_text.get()
        img_file = self.img_fileselector.file_text.get()
        anno_file = self.geojson_fileselector.file_text.get()
         
        if img_file == '' or mat_file == '' or anno_file == '':
            cprint("All files must be set! Objects not set!", "red")
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
        self.bucketed_frame.pack_forget()
        
        cprint("Clearing the object!", 'cyan')

    def finalize_image(self):
        self.backend.DRAW_HELPER.reset()
    
        if(self.draw_annotations_var.get()):
            cprint("Drawing them ANNOTATIONS brother", 'magenta')
            if self.draw_annotations_textbox.get():
                values_to_draw = [x.strip() for x in self.draw_annotations_textbox.get().split(',')]

                anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(values_to_draw)
                self.backend.DRAW_HELPER.draw_annotations(
                    self.backend.ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes),
                    draw_anno_indexes=self.draw_annotations_info_var.get()) # draw_anno_indexes = False
            else:
                self.backend.DRAW_HELPER.draw_annotations(self.backend.ANNOTATION_HELPER.annotations,
                                                          draw_anno_indexes=self.draw_annotations_info_var.get()) # draw_anno_indexes = False

        if(self.draw_fibers_var.get()):
            cprint("Drawing them FIBERS brother", 'magenta')
            verts = self.backend.CTF_OUTPUT.fibers
            widths = self.backend.CTF_OUTPUT.fiber_widths
            if(self.backend.bucketed_fibers is not None and self.draw_fibers_textbox.get()):
                fiber_zones = self.split_string_to_ints(self.draw_fibers_textbox.get())
                self.backend.DRAW_HELPER.draw_fibers_per_zone(verts, widths, self.backend.bucketed_fibers, fiber_zones)
            else:
                self.backend.DRAW_HELPER.draw_fibers(verts, widths)
                
        if(self.backend.bucketed_fibers is not None):
            if(self.draw_zones_var.get()):
                cprint("Drawing them ZONES brother", 'magenta')
                zone_boundaries = [0, 50, 150]
                if(self.csv_boundaries_text.get()):
                    zone_boundaries = self.split_string_to_ints(self.csv_boundaries_text.get())

                annotations_to_draw = []
                if self.bucket_fibers_text.get():
                    annotations_to_draw = [x.strip() for x in self.bucket_fibers_text.get().split(',')]
                anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_draw)
                zones = self.backend.ANNOTATION_HELPER.get_final_union_zones(zone_boundaries, anno_indexes)

                to_draw = list(np.arange(len(zones)))
                if(self.draw_zones_textbox.get()):
                    cprint(f'Cancer {self.draw_zones_textbox.get()}', 'cyan')
                    to_draw = self.split_string_to_ints(self.draw_zones_textbox.get())
                self.backend.DRAW_HELPER.draw_zone_outlines(zones, to_draw=to_draw) #  to_draw=[1, 3]
                # self.backend.DRAW_HELPER.draw_zones(zones, to_draw=to_draw) #  to_draw=[1, 3]

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
                                                filetypes=[("TIFF", "*.tif")])
        if filename:
            self.finalize_image()
            self.backend.DRAW_HELPER.save_file_overlay(filename)
            self.save_image_textbox.delete(0, tk.END)
            self.save_image_textbox.insert(0, filename)

    def bucket_the_fibers(self):
        """Note: This function is threaded because the bucketing is not the fastest thing in the west"""
        if(self.backend):
            self.bucket_fibers_label.config(text='Bucketing Fibers...!', fg= "orange")
            fibers = self.backend.CTF_OUTPUT.fibers
            centroids = self.backend.CTF_OUTPUT.centroids
            
            annotations_to_draw = []
            if self.bucket_fibers_text.get():
                annotations_to_draw = [x.strip() for x in self.bucket_fibers_text.get().split(',')]

            anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_draw)
            annotations_to_use = self.backend.ANNOTATION_HELPER.get_annotations_from_indexes(anno_indexes)
                
            zone_boundaries = [0, 50, 150]
            if(self.csv_boundaries_textbox.get()):
                zone_boundaries = self.split_string_to_ints(self.csv_boundaries_textbox.get())
            
            def bucket_fibers():
                self.backend.bucket_the_fibers(fibers, centroids, annotations_to_use, zone_boundaries)
                self.backend.annotations_indexes_bucketed_on = anno_indexes 
                self.bucket_fibers_label.config(text='Fibers currently BUCKETED!', fg= "green")
                self.widgets_to_display_after_bucketing()
                
            threading.Thread(target=bucket_fibers).start() 

    def display_averages(self):
        width_avgs, len_avgs, ang_avgs, zone_bounds = self.calc_averages()
        zone_bound_len = len(zone_bounds) + 1
        
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
        zone_boundaries = [0, 50, 150]
        if(self.csv_boundaries_text.get()):
            zone_boundaries = self.split_string_to_ints(self.csv_boundaries_text.get())
        zone_bound_len = len(zone_boundaries) + 1
        print(f"HERE IS THE ZONE BOUNDARY: {zone_boundaries, self.csv_boundaries_text.get()}")
        
        widths = self.backend.CTF_OUTPUT.fiber_widths
        width_avgs = get_average_value_per_zone(widths, self.backend.bucketed_fibers, zone_bound_len)
        width_avgs[-1] = np.mean(widths)
        
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths()
        len_avgs = get_average_value_per_zone(lengths, self.backend.bucketed_fibers, zone_bound_len)
        len_avgs[-1] = np.mean(lengths)
        
        angles = self.backend.CTF_OUTPUT.fiber_angles
        ang_avgs = get_average_value_per_zone(angles, self.backend.bucketed_fibers, zone_bound_len)
        ang_avgs[-1] = np.mean(angles)
        
        return width_avgs, len_avgs, ang_avgs, zone_boundaries

    def display_signal_densities(self):
        sig_dens, zone_boundaries = self.calc_signal_densities()
        sig_dens_str = "\nSignal Densities:"
        for i in range(len(zone_boundaries) + 1):
            sig_dens_str+= f"\n\tZone {i}: signal density: {'{0:.2%}'.format(sig_dens[i])}"
        msg_box.showinfo("Signla Density Info", sig_dens_str)
        sig_dens_str+=f"\n\tList Form: {sig_dens}\n"
        # tab_list = str(sig_dens).replace(',', '\t')
        # sig_dens_str+=f"\tList Form: {tab_list}\n"
        cprint(sig_dens_str, 'cyan')

    def calc_signal_densities(self):
        cprint("Calculating Signal Density", 'magenta')
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths()
        widths = self.backend.CTF_OUTPUT.fiber_widths
        
        zone_boundaries = [0, 50, 150]
        if(self.csv_boundaries_text.get()):
            zone_boundaries =  self.split_string_to_ints(self.csv_boundaries_text.get())
        
        annotations_to_draw = []
        if self.bucket_fibers_text.get():
            annotations_to_draw = [x.strip() for x in self.bucket_fibers_text.get().split(',')]
        anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_draw)
        zones = self.backend.ANNOTATION_HELPER.get_final_union_zones(zone_boundaries, anno_indexes)
            
        sig_dens = get_signal_density_overall(lengths, widths, zones, self.backend.bucketed_fibers)
        return sig_dens, zone_boundaries
    
    def display_combination_signal_densities(self):
        singnal_dens_only_stromal, zones_to_combo = self.calc_combination_signal_densities()
        
        combo_sig_dens_str = "\nSignal Densities:"
        combo_sig_dens_str+= f"\n\tZone {zones_to_combo}: signal density: {'{0:.2%}'.format(singnal_dens_only_stromal)}"
        msg_box.showinfo("Signla Density Info", combo_sig_dens_str)
        cprint(combo_sig_dens_str, 'cyan')

    def calc_combination_signal_densities(self):
        cprint("Calculating Combination Signal Density", 'magenta')
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths()
        widths = self.backend.CTF_OUTPUT.fiber_widths
        
        zone_boundaries = [0, 50, 150]
        if(self.csv_boundaries_text.get()):
            zone_boundaries =  self.split_string_to_ints(self.csv_boundaries_text.get())
        
        annotations_to_draw = []
        if self.bucket_fibers_text.get():
            annotations_to_draw = [x.strip() for x in self.bucket_fibers_text.get().split(',')]
        anno_indexes = self.backend.ANNOTATION_HELPER.get_annotation_indexes(annotations_to_draw)
        zones = self.backend.ANNOTATION_HELPER.get_final_union_zones(zone_boundaries, anno_indexes)
     
        zones_to_combo = list(range(len(zones)))
        if(self.get_combo_signal_densities_textbox.get()):
            zones_to_combo =  self.split_string_to_ints(self.get_combo_signal_densities_textbox.get())
        singnal_dens_only_stromal = get_signal_density_per_desired_zones(lengths, widths, zones, self.backend.bucketed_fibers, zones_to_combo)
        self.backend.combo_zones_numbers[str(zones_to_combo)] = singnal_dens_only_stromal
        return singnal_dens_only_stromal, zones_to_combo
          
    def split_string_to_ints(self, textbox_value):
        try:
            to_ret = [] 
            for x in textbox_value.split(','):
                if(x.strip()):
                    to_ret.append(int(x.strip()))
            return to_ret
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
        annotations_to_use = self.backend.ANNOTATION_HELPER.get_annotations_from_indexes(self.backend.annotations_indexes_bucketed_on)
        return get_signal_density_for_all_annotations(self.backend.bucketed_fibers, 
                                                      annotations_to_use, lengths, widths)
    
    def export_info(self):
        print(f"Exporting Information to {self.export_info_text.get()}...")
       
        filename = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("text", "*.txt")])
        if filename:
            self.export_info_text.set(filename)    
            np.savetxt(filename, self.backend.bucketed_fibers, delimiter='\t')
    
            if(self.export_compressed_bool.get()):
                self.export_info_text.set(filename)    
                np.save(f"{os.path.splitext(filename)[0]}.npy", self.backend.bucketed_fibers)
                    
            width_avgs, len_avgs, ang_avgs, zone_bounds = self.calc_averages()
            sig_dens, zone_boundaries = self.calc_signal_densities()

            if(self.bucket_fibers_text.get()):
                annotations_selected = self.bucket_fibers_text.get()
            else:
                annotations_selected = 'ALL'
                
            test_dict = {
                'Averages': {
                    'Widths': list(width_avgs.values()),
                    'Lengths': list(len_avgs.values()),
                    'Angles': list(ang_avgs.values()),
                },
                'Signal Densities per Annotation': list(self.calc_sig_dens_per_anno()),
                'Signal Densities': sig_dens,
                'Zones': zone_bounds,
                'Annotations Bucketed On': annotations_selected,
                'Annotation Indexes Bucketed On': self.backend.annotations_indexes_bucketed_on,
                'Combination Signal Densities': self.backend.combo_zones_numbers,
                'GeoJson File': self.geojson_fileselector.file_text.get(),
                'Mat File': self.mat_fileselector.file_text.get(),
                'Img File': self.img_fileselector.file_text.get()
            }
            with open(f"{os.path.splitext(filename)[0]}.json", 'w') as fp:
                json.dump(test_dict, fp, sort_keys=True, indent=2)
            
            self.save_as_tsv(test_dict, filename)
                # filename = fd.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
    
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
                    print(f"{key}\t{value}")
                    tsv_data += f"{key}\t{value}\n"
        tsv_data+='\n'
        with open(f"{os.path.splitext(filename)[0]}.tsv", 'w') as file:
            file.write(tsv_data)
    
    def display_as_array_to_copy(self, dict):
        return str(list(dict.values())).replace(',',  '\t')
    
    def import_info(self):
        print("Importing the info")
        filename = fd.askopenfilename(title='Open a file', filetypes=[('JSON files', '*.json')])
        if filename:
            self.import_text.set(filename)
            with open(filename) as fp:
                data = json.load(fp)
                print(data)
            if('Img File' in data):
                self.clear_object()
                self.mat_fileselector.file_text.set(data['Mat File']) 
                self.img_fileselector.file_text.set(data['Img File'])
                self.geojson_fileselector.file_text.set(data['GeoJson File']) 
                
                self.backend = GUI_Helper(data['Img File'], data['Mat File'], data['GeoJson File'])
                self.widgets_to_display_after_obj_set()
                cprint("All objects set!", "cyan")
                
                if os.path.isfile(f"{os.path.splitext(filename)[0]}.npy"):
                    self.backend.bucketed_fibers = np.load(f"{os.path.splitext(filename)[0]}.npy")
                    self.bucket_fibers_label.config(text='Fibers currently BUCKETED!', fg= "green")
                    self.widgets_to_display_after_bucketing()
                    
                    if('Zones' in data):
                        self.csv_boundaries_text.set(str(data['Zones'])[1:-1])
                    
                    if('Annotations Bucketed On' in data):
                        anno_info = data['Annotations Bucketed On']
                        if(anno_info != 'ALL'):
                            self.bucket_fibers_text.set(anno_info)
                    cprint("Bucketed Fibers Loaded", "cyan")
            
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
                    print(f"{corrected_point} - {anno} \nSignal Density: {get_signal_density_per_annotation(self.gui_helper.bucketed_fibers[:, anno.original_index], self.gui_helper.ANNOTATION_HELPER.annotations[anno.original_index], lengths, widths)}\n")

        # For the 2nd annotation
        
                # draw = ImageDraw.Draw(self.img_copy)
                # draw.polygon(anno.geo_polygon.exterior.coords, outline='red')
                # del draw
                # # Update the displayed image
                # self.image = self.img_copy.resize((self.image.size[0], self.image.size[1]))
                # self.background_image = ImageTk.PhotoImage(self.image)
                # self.background.configure(image =  self.background_image)
                # break
                 
                  
def main(): 
    root = Tk()
    root.title("DCIS Helper")
    root.geometry("900x750")

    # sv_ttk.set_theme("dark")
    
    menu_window = MainFrame(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()
