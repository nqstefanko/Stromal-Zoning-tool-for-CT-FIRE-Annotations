import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import tkinter.messagebox as msg_box
from PIL import ImageTk, Image  
from tkinter import *
import threading

from PIL import Image, ImageTk
import os, sys

from ctfire_output_helper import CTFIREOutputHelper
from annotation_helper import AnnotationHelper
from test_export import *
from termcolor import cprint, colored

import sv_ttk

IMG_FILETYPES = (
    ('TIFF files', '*.tif'),
    ('JPEG files', '*.jpg'),
    ('PNG files', '*.png'),
    ('All files', '*.*')
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
        self.fileselector_frame = tk.Frame(self.master)
        self.frame = tk.Frame(self.master)
        self.bucketed_frame = tk.Frame(self.master, bg='green')
        self.display_save_frame = tk.Frame(self.master)
        self.checkbox_frame = tk.Frame(self.master)

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
        
        # Frames
        self.fileselector_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
     
    def widgets_to_display_after_obj_set(self):
        #ZONES Entry
        self.csv_boundaries_label = tk.Label(self.frame, text="CSV boundaries of zones (Default: 0, 50, 150):")
        self.csv_boundaries_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")

        self.csv_boundaries_textbox = tk.Entry(self.frame)
        self.csv_boundaries_textbox.grid(row=0, column=1, padx=5, pady=5)

        # Draw Annotations
        self.draw_annotations_var = tk.BooleanVar()
        self.draw_annotations_checkbox = tk.Checkbutton(self.frame, text="Draw Annotations", variable=self.draw_annotations_var)
        self.draw_annotations_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="W")

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

        self.bucket_fibers_textbox = tk.Entry(self.frame)
        self.bucket_fibers_textbox.grid(row=4, column=1, padx=5, pady=5, sticky="W")

        self.bucket_fibers_description_label = tk.Label(self.frame, text="- CSV Annotations Names to bucket on (Default: All)")
        self.bucket_fibers_description_label.grid(row=4, column=2, padx=5, pady=5, sticky="W")
        
        self.bucket_fibers_label = tk.Label(self.frame, text="Fibers currently UNBUCKETED!", fg= "red")
        self.bucket_fibers_label.grid(row=5,padx=5, pady=5, sticky="W")
        
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
        self.get_averages_button = tk.Button(self.bucketed_frame, text='Calculate Averages', command=self.calc_averages)
        self.get_averages_button.grid(row=2, padx=5, pady=5, sticky="W")
        
        # Calculate the Signal Densities Button:
        self.get_signal_densities_button = tk.Button(self.bucketed_frame, text='Calculate Signal Densities', command=self.calc_signal_densities)
        self.get_signal_densities_button.grid(row=3, padx=5, pady=5, sticky="W")
        
        # Calculate the Combination:
        self.get_combo_signal_densities_button = tk.Button(self.bucketed_frame, text='Calculate Combination Signal Densities', command=self.calc_combination_signal_densities)
        self.get_combo_signal_densities_button.grid(row=4, padx=5, pady=5, sticky="W")
        
        self.get_combo_signal_densities_textbox = tk.Entry(self.bucketed_frame)
        self.get_combo_signal_densities_textbox.grid(row=4, column=1, padx=5, pady=5)
        
        self.get_combo_signal_densities_label = tk.Label(self.bucketed_frame, text="- CSV values for zones to combine (Default: All)")
        self.get_combo_signal_densities_label.grid(row=4, column=2, padx=5, pady=5, sticky="W")
        
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
                self.backend.DRAW_HELPER.draw_annotations(self.backend.ANNOTATION_HELPER.get_specific_annotations(values_to_draw)) # draw_anno_indexes = False
            else:
                self.backend.DRAW_HELPER.draw_annotations(self.backend.ANNOTATION_HELPER.annotations) # draw_anno_indexes = False

        if(self.draw_fibers_var.get()):
            cprint("Drawing them FIBERS brother", 'magenta')
            verts = self.backend.CTF_OUTPUT.get_fiber_vertices_thresholded()
            widths = self.backend.CTF_OUTPUT.get_fiber_widths_thresholded()
            if(self.backend.bucketed_fibers is not None and self.draw_fibers_textbox.get()):
                fiber_zones = self.split_string_to_ints(self.draw_fibers_textbox.get())
                self.backend.DRAW_HELPER.draw_fibers_per_zone(verts, widths, self.backend.bucketed_fibers, fiber_zones)
            else:
                self.backend.DRAW_HELPER.draw_fibers(verts, widths)
                
        if(self.backend.bucketed_fibers is not None):
            if(self.draw_zones_var.get()):
                cprint("Drawing them ZONES brother", 'magenta')
                zone_boundaries = [0, 50, 150]
                if(self.csv_boundaries_textbox.get()):
                    zone_boundaries = self.split_string_to_ints(self.csv_boundaries_textbox.get())

                annotations_to_use = []
                if self.bucket_fibers_textbox.get():
                    annotations_to_use = [x.strip() for x in self.bucket_fibers_textbox.get().split(',')]
                zones = self.backend.ANNOTATION_HELPER.get_final_zones(zone_boundaries, annotations_to_use)

                to_draw = list(np.arange(len(zones)))
                if(self.draw_zones_textbox.get()):
                    cprint(f'Cancer {self.draw_zones_textbox.get()}', 'cyan')
                    to_draw = self.split_string_to_ints(self.draw_zones_textbox.get())
                self.backend.DRAW_HELPER.draw_zone_outlines(zones, to_draw=to_draw) #  to_draw=[1, 3]

    def display_image(self):
        filename = self.img_fileselector.file_text.get()
        if(self.backend):
            self.finalize_image()
            self.newWindow = tk.Toplevel(self.master)
            self.app = ImageWindow(self.newWindow, image=self.backend.DRAW_HELPER.get_image())
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
        
    def new_window(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = ImageWindow(self.newWindow)

    def bucket_the_fibers(self):
        """Note: This function is threaded because the bucketing is not the fastest thing in the west"""
        if(self.backend):
            self.bucket_fibers_label.config(text='Bucketing the Fibers...!', fg= "orange")
            fibers = self.backend.CTF_OUTPUT.get_fiber_vertices_thresholded()
            centroids = self.backend.CTF_OUTPUT.get_centroids()
            if self.bucket_fibers_textbox.get():
                values_to_draw = [x.strip() for x in self.bucket_fibers_textbox.get().split(',')]
                annotations_to_use = self.backend.ANNOTATION_HELPER.get_specific_annotations(values_to_draw)
            else:
                annotations_to_use = self.backend.ANNOTATION_HELPER.annotations
            
            zone_boundaries = [0, 50, 150]
            if(self.csv_boundaries_textbox.get()):
                zone_boundaries = self.split_string_to_ints(self.csv_boundaries_textbox.get())
            
            def bucket_fibers():
                self.backend.bucket_the_fibers(fibers, centroids, annotations_to_use, zone_boundaries)
                self.bucket_fibers_label.config(text='Fibers currently BUCKETED!', fg= "green")
                self.widgets_to_display_after_bucketing()
                
            threading.Thread(target=bucket_fibers).start() 

    def calc_averages(self):
        zone_boundaries = [0, 50, 150]
        if(self.csv_boundaries_textbox.get()):
            zone_boundaries = self.split_string_to_ints(self.csv_boundaries_textbox.get())
        zone_bound_len = len(zone_boundaries) + 1
        
        print("Calcing Averages")
        widths = self.backend.CTF_OUTPUT.get_fiber_widths()
        width_avgs = get_average_value_per_zone(widths, self.backend.bucketed_fibers, zone_bound_len)
        width_avg_str = "Width Averages: \n"

        print(f"HERE IS THE ZONE BOUNDARY: {zone_boundaries, self.csv_boundaries_textbox.get()}")
        
        for i in range(zone_bound_len):
            width_avg_str+=f"\t Zone {i} width averages: {width_avgs[i]}\n"
        width_avg_str+=f"\t Total Average Width {np.mean(widths)}\n"
        msg_box.showinfo("Width Info", width_avg_str)

        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths_thresholded()
        len_avgs = get_average_value_per_zone(lengths, self.backend.bucketed_fibers, zone_bound_len)
        len_avg_str = "Length Averages: \n"
        for i in range(zone_bound_len):
            len_avg_str+=f"\t Zone {i} length averages: {len_avgs[i]}\n"
        len_avg_str+=f"\t Total Average Length {np.mean(lengths)}\n"
        msg_box.showinfo("Length Info", len_avg_str)
            
        angles = self.backend.CTF_OUTPUT.get_fiber_angles()
        ang_avgs = get_average_value_per_zone(angles, self.backend.bucketed_fibers, zone_bound_len)
        ang_avg_str = "Angle Averages: \n"
        for i in range(zone_bound_len):
            ang_avg_str+=f"\t Zone {i} angle averages: {ang_avgs[i]}\n"
        ang_avg_str+=f"\t Total Average Angle {np.mean(angles)}\n"
        
        msg_box.showinfo("Angle Info", ang_avg_str)
        
        cprint(width_avg_str, 'yellow')
        cprint(len_avg_str, 'cyan')
        cprint(ang_avg_str, 'magenta')

    def calc_signal_densities(self):
        cprint("Calculating Signal Density", 'magenta')
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths_thresholded()
        widths = self.backend.CTF_OUTPUT.get_fiber_widths_thresholded()
        
        zone_boundaries = [0, 50, 150]
        if(self.csv_boundaries_textbox.get()):
            zone_boundaries =  self.split_string_to_ints(self.csv_boundaries_textbox.get())
        
        annotations_to_use = []
        if self.bucket_fibers_textbox.get():
            annotations_to_use = [x.strip() for x in self.bucket_fibers_textbox.get().split(',')]
        
        print(f"{zone_boundaries, len(annotations_to_use)}")
        
        zones = self.backend.ANNOTATION_HELPER.get_final_zones(zone_boundaries, annotations_to_use)
        sig_dens = get_signal_density_overall(lengths, widths, zones, self.backend.bucketed_fibers)
        sig_dens_str = "\nSignal Densities:"
        for i in range(len(zone_boundaries) + 1):
            sig_dens_str+= f"\n\tZone {i}: signal density: {'{0:.2%}'.format(sig_dens[i])}"
        
        msg_box.showinfo("Signla Density Info", sig_dens_str)
        cprint(sig_dens_str, 'cyan')

    def calc_combination_signal_densities(self):
        cprint("Calculating Combination Signal Density", 'magenta')
        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths_thresholded()
        widths = self.backend.CTF_OUTPUT.get_fiber_widths_thresholded()
        
        zone_boundaries = [0, 50, 150]
        if(self.csv_boundaries_textbox.get()):
            zone_boundaries =  self.split_string_to_ints(self.csv_boundaries_textbox.get())
        
        annotations_to_use = []
        if self.bucket_fibers_textbox.get():
            annotations_to_use = [x.strip() for x in self.bucket_fibers_textbox.get().split(',')]

        zones = self.backend.ANNOTATION_HELPER.get_final_zones(zone_boundaries, annotations_to_use)
     
        zones_to_combo = list(range(len(zones)))
        if(self.get_combo_signal_densities_textbox.get()):
            zones_to_combo =  self.split_string_to_ints(self.get_combo_signal_densities_textbox.get())
            
        singnal_dens_only_stromal = get_singal_density_per_desired_zones(lengths, widths, zones, self.backend.bucketed_fibers, zones_to_combo)
        combo_sig_dens_str = "\nSignal Densities:"
        combo_sig_dens_str+= f"\n\tZone {zones_to_combo}: signal density: {'{0:.2%}'.format(singnal_dens_only_stromal)}"
        msg_box.showinfo("Signla Density Info", combo_sig_dens_str)
        cprint(combo_sig_dens_str, 'cyan')
        
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
        
class ImageWindow:
    def __init__(self, master, filename=None, image=None):
        self.master = master
        self.frame = Frame(self.master)
        if(filename):
            self.image = Image.open(filename)
        else:
            self.image = image
        self.img_copy= self.image.copy()

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
        
    def _resize_image(self,event):
        new_width = event.width
        new_height = event.height

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image =  self.background_image)

def main(): 
    root = Tk()
    root.title("DCIS Helper")
    root.geometry("900x600")

    # sv_ttk.set_theme("dark")
    
    menu_window = MainFrame(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()
    
