# # #CROPPED_IMG DATA
# TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.tif"
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout\ctFIREout_2B_D9_crop2.mat"
# EXPORTED_ANNOTATION_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\2B_D9_crop2.geojson"

# #18 DENOISED DATA 18
# EXPORTED_ANNOTATION_FILEPATH = os.path.join(sys.path[0], "./ANNOTATED-DCIS-018_10x10_1_Nuclei_Collagen - Denoised.geojson")
# TIF_FILEPATH = os.path.join(sys.path[0], "../Denoised_images/DCIS-018_10x10_1_Nuclei_Collagen - Denoised.tif")
# MAT_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\Denoised_images\ctFIREout\ctFIREout_DCIS-018_10x10_1_Nuclei_Collagen - Denoised_s1.mat"

#Tests
# TIF_FILEPATH = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\DCIS_Collagen_Collaboration\dcis_code\bongbong.tif"

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

class FileSelectorManager():
    pass
    
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

class MenuWindow: 
    def __init__(self, master):
        self.master = master
        self.fileselector_frame = tk.Frame(self.master)
        self.frame = tk.Frame(self.master)
        self.checkbox_frame = tk.Frame(self.master)

        self.backend = None
        
        # FILE SELECTORS
        self.img_fileselector = FileSelector(self.fileselector_frame, "Upload Image...", 0, IMG_FILETYPES) 
        self.mat_fileselector = FileSelector(self.fileselector_frame, "Upload .mat file...", 1, MATLAB_FILETYPES)     
        self.geojson_fileselector = FileSelector(self.fileselector_frame, "Upload GeoJson...", 2, GEOJSON_FILETYPES)
        
        # Create a button to display the UNEDITED image
        self.display_button = tk.Button(self.fileselector_frame, text='Display Unedited Image', command=self.display_image)
        self.display_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Create a button to set the GUI_Helper Object
        self.set_up_object_button = tk.Button(self.fileselector_frame, text='Set Up Objects', command=self.set_objects)
        self.set_up_object_button.grid(row=4)
        
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

        self.draw_fibers_textbox = tk.Entry(self.frame)
        self.draw_fibers_textbox.grid(row=2, column=1, padx=5, pady=5)
        self.draw_fibers_label = tk.Label(self.frame, text="- CSV values for zones of fibers to draw (Default: All)")
        self.draw_fibers_label.grid(row=2, column=2, padx=5, pady=5, sticky="W")

        # Draw Zones
        self.draw_zones_var = tk.BooleanVar()
        self.draw_zones_checkbox = tk.Checkbutton(self.frame, text="Draw Zones", variable=self.draw_zones_var)
        self.draw_zones_checkbox.grid(row=3, column=0, padx=5, pady=5, sticky="W")
        
        self.draw_zones_textbox = tk.Entry(self.frame)
        self.draw_zones_textbox.grid(row=3, column=1, padx=5, pady=5)
        self.draw_zones_label = tk.Label(self.frame, text="- CSV values for zones to draw (Default: All)")
        self.draw_zones_label.grid(row=3, column=2, padx=5, pady=5, sticky="W")

        # Bucket Fibers Bucket
        self.bucket_fibers_button = tk.Button(self.frame, text='Bucket the Fibers', command=self.bucket_the_fibers)
        self.bucket_fibers_button.grid(row=4, column=0, padx=5, pady=5, sticky="W")

        self.bucket_fibers_textbox = tk.Entry(self.frame)
        self.bucket_fibers_textbox.grid(row=4, column=1, padx=5, pady=5, sticky="W")

        self.bucket_fibers_description_label = tk.Label(self.frame, text="- CSV Annotations Names to bucket on (Default: All)")
        self.bucket_fibers_description_label.grid(row=4, column=2, padx=5, pady=5, sticky="W")
        
        self.bucket_fibers_label = tk.Label(self.frame, text="Fibers currently UNBUCKETED!", fg= "red")
        self.bucket_fibers_label.grid(row=5,padx=5, pady=5, sticky="W")
        
        # Display Edited Image Button
        self.display_edited_image_button = tk.Button(self.frame, text='Display Edited Image', command=self.display_image)
        self.display_edited_image_button.grid(row=6, padx=5, pady=5, sticky="W")
        
        # Calculate the averages please:
        self.get_averages_button = tk.Button(self.frame, text='Calculate Averages', command=self.calc_averages)
        self.get_averages_button.grid(row=7, padx=5, pady=5, sticky="W")
        
        # Frames
        self.fileselector_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
        # self.checkbox_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
        self.frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
        
    def set_everything_else(self):        
        # Create final saver of images
        self.save_label = tk.Label(self.fileselector_frame, text="Save Image...")
        self.save_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.save_text = tk.StringVar()
        self.save_entry = tk.Entry(self.fileselector_frame, textvariable=self.save_text, width=50)
        self.save_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.save_button = tk.Button(self.fileselector_frame, text='Save Image', command=self.save_image)
        self.save_button.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        self.file_clear_button = tk.Button(self.fileselector_frame, text='Clear', command=self.save_image)
        self.file_clear_button.grid(row=3, column=3, padx=5, pady=5)
        
        # Create Spinbox to display number of zones
        self.num_zones_label = tk.Label(self.checkbox_frame, text="Number of Zones:")
        self.num_zones_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.num_zones_spinbox = tk.Spinbox(self.checkbox_frame, from_=0, to=10, width=5, command=self.show_checkboxes)
        self.num_zones_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.num_zones_spinbox.delete(0, "end")
        self.num_zones_spinbox.insert(0, 0)
        
        self.show_checkboxes(1)

        # Checkboxes and textboxes
        self.draw_annotations_var = tk.BooleanVar()
        self.draw_annotations_checkbox = tk.Checkbutton(self.frame, text="Draw Annotations", variable=self.draw_annotations_var)
        self.draw_annotations_checkbox.config(selectcolor='green')
        
        self.draw_annotations_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="W")

        self.draw_annotations_textbox = tk.Entry(self.frame)
        self.draw_annotations_textbox.grid(row=0, column=1, padx=5, pady=5)

        self.draw_fibers_var = tk.BooleanVar()
        self.draw_fibers_checkbox = tk.Checkbutton(self.frame, text="Draw Fibers", variable=self.draw_fibers_var)
        self.draw_fibers_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="W")

        self.draw_zones_var = tk.BooleanVar()
        self.draw_zones_checkbox = tk.Checkbutton(self.frame, text="Draw Zones", variable=self.draw_zones_var)
        self.draw_zones_checkbox.config(selectcolor='green')
        self.draw_zones_checkbox.grid(row=2, column=0, padx=5, pady=5, sticky="W")

        self.draw_zones_textbox = tk.Entry(self.frame)
        self.draw_zones_textbox.grid(row=2, column=1, padx=5, pady=5)

    def set_objects(self):
        mat_file = self.mat_fileselector.file_text.get()
        img_file = self.img_fileselector.file_text.get()
        anno_file = self.geojson_fileselector.file_text.get()
         
        if img_file == '' or mat_file == '' or anno_file == '':
            cprint("All files must be set! Objects not set!", "red")
            return 

        self.backend = GUI_Helper(img_file, mat_file, anno_file)
        cprint("All objects set!", "cyan")

    def show_checkboxes(self, starting_row=7):
        # Remove existing checkboxes and entries
        for widget in self.checkbox_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton) or isinstance(widget, tk.Entry):
                widget.destroy()

        # Create new checkboxes and entries based on the selected number of zones
        num_zones = int(self.num_zones_spinbox.get())
        if num_zones > 0:
            self.vars = []
            self.entries = []
            for i in range(num_zones):
                index = starting_row + i
                var = IntVar()
                check = tk.Checkbutton(self.checkbox_frame, text=f"Zone {i+1}", variable=var)
                check.config(selectcolor='green')
                check.grid(row=index, column=0, padx=5, pady=2, sticky=tk.W)
                self.vars.append(var)

                entry = tk.Entry(self.checkbox_frame, width=5, state=tk.DISABLED)
                entry.grid(row=index, column=1, padx=5, pady=2, sticky=tk.W)
                self.entries.append(entry)

                # bind the checkbox to a function that enables/disables the entry widget
                check.config(command=lambda idx=i: self.entries[idx].config(state=tk.NORMAL if self.vars[idx].get() else tk.DISABLED))

    def finalize_image(self):
        self.backend.DRAW_HELPER.reset()
    
        if(self.draw_annotations_var.get()):
            cprint("Drawing them ANNOTATIONS brother", 'magenta')
            if self.draw_annotations_textbox.get():
                values_to_draw = [x for x in self.draw_annotations_textbox.get().split(',')]
                self.backend.DRAW_HELPER.draw_annotations(self.backend.ANNOTATION_HELPER.get_specific_annotations(values_to_draw)) # draw_anno_indexes = False
            else:
                self.backend.DRAW_HELPER.draw_annotations(self.backend.ANNOTATION_HELPER.annotations) # draw_anno_indexes = False

        if(self.draw_fibers_var.get()):
            cprint("Drawing them FIBERS brother", 'magenta')
            verts = self.backend.CTF_OUTPUT.get_fiber_vertices_thresholded()
            widths = self.backend.CTF_OUTPUT.get_fiber_widths_thresholded()
            
            if(self.draw_fibers_textbox.get()):
                fiber_zones = [int(x) for x in self.draw_fibers_textbox.get().split(',')]
                print("Heyo fiber zones:", fiber_zones, self.backend.bucketed_fibers.shape)
                self.backend.DRAW_HELPER.draw_fibers_per_zone(verts, widths, self.backend.bucketed_fibers, fiber_zones)
            else:
                self.backend.DRAW_HELPER.draw_fibers(verts, widths)

        if(self.draw_zones_var.get()):
            cprint("Drawing them ZONES brother", 'magenta')
            zone_boundaries = [0, 50, 150]
            if(self.csv_boundaries_textbox.get()):
                zone_boundaries = [int(x) for x in self.csv_boundaries_textbox.get().split(',')]

            annotations_to_use = []
            if self.bucket_fibers_textbox.get():
                annotations_to_use = [x for x in self.bucket_fibers_textbox.get().split(',')]
            zones = list(reversed(self.backend.ANNOTATION_HELPER.get_final_zones(zone_boundaries, annotations_to_use)))

            to_draw = np.arange(len(zones))
            if(self.draw_zones_textbox.get()):
                cprint(f'Cancer {self.draw_zones_textbox.get()}', 'cyan')
                to_draw = [int(x) for x in self.draw_zones_textbox.get().split(',')]
            self.backend.DRAW_HELPER.draw_zones(zones, to_draw=to_draw) #  to_draw=[1, 3]

    def display_image(self):
        filename = self.img_fileselector.file_text.get()
        if(self.backend):
            self.finalize_image()
            self.newWindow = tk.Toplevel(self.master)
            self.app = ImageWindow(self.newWindow, image=self.backend.DRAW_HELPER.get_image())
        elif filename:
            self.newWindow = tk.Toplevel(self.master)
            self.app = ImageWindow(self.newWindow, filename)

    def save_image(self):
        print("Saving Image")

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
                values_to_draw = [x for x in self.bucket_fibers_textbox.get().split(',')]
                annotations_to_use = self.backend.ANNOTATION_HELPER.get_specific_annotations(values_to_draw)
            else:
                annotations_to_use = self.backend.ANNOTATION_HELPER.annotations
            
            def bucket_fibers():
                self.backend.bucket_the_fibers(fibers, centroids, annotations_to_use)
                self.bucket_fibers_label.config(text='Fibers currently BUCKETED!', fg= "green")
                
            threading.Thread(target=bucket_fibers).start() 

    def calc_averages(self):
        print("Calcing Averages")
        widths = self.backend.CTF_OUTPUT.get_fiber_widths()
        width_avgs = get_average_width_per_zone(widths, self.backend.bucketed_fibers)
        width_avg_str = "Width Averages: \n"
        for i in range(4):
            width_avg_str+=f"\t Zone {i} width averages: {width_avgs[i]}\n"
        msg_box.showinfo("showinfo", width_avg_str)


        lengths = self.backend.CTF_OUTPUT.get_fiber_lengths_thresholded()
        len_avgs = get_average_length_per_zone(lengths, self.backend.bucketed_fibers)
        len_avg_str = "Length Averages: \n"
        for i in range(4):
            len_avg_str+=f"\t Zone {i} length averages: {len_avgs[i]}\n"
        msg_box.showinfo("showinfo", len_avg_str)
            
        angles = self.backend.CTF_OUTPUT.get_fiber_angles()
        ang_avgs = get_average_angle_per_zone(angles, self.backend.bucketed_fibers)
        ang_avg_str = "Angle Averages: \n"
        for i in range(4):
            ang_avg_str+=f"\t Zone {i} angle averages: {ang_avgs[i]}\n"
        msg_box.showinfo("showinfo", ang_avg_str)
        
        cprint(width_avg_str, 'yellow')
        cprint(len_avg_str, 'cyan')
        cprint(ang_avg_str, 'magenta')

            
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
    
    menu_window = MenuWindow(root)
    root.mainloop()
    

if __name__ == '__main__':
    main()
    

        




# class ImageWindow(Frame):
#     def __init__(self, master, *pargs):
#         Frame.__init__(self, master, *pargs)

#         self.image = Image.open(TIF_FILEPATH)
#         self.img_copy= self.image.copy()

#         self.background_image = ImageTk.PhotoImage(self.image)

#         self.background = Label(self, image=self.background_image)
#         self.background.pack(fill=BOTH, expand=YES)
#         self.background.bind('<Configure>', self._resize_image)

#     def _resize_image(self,event):

#         new_width = event.width
#         new_height = event.height

#         self.image = self.img_copy.resize((new_width, new_height))

#         self.background_image = ImageTk.PhotoImage(self.image)
#         self.background.configure(image =  self.background_image)
# e = ImageWindow(root)
# e.pack(fill=BOTH, expand=YES)

# button1 = Button(root, text='Hello')
# # button that would displays the plot
# plot_button = Button(master = root, height = 2, width = 10, text = "Plot")
# # place the button into the window
# plot_button.pack()

# menu_window = MenuWindow(root)
# menu_window.pack(fill=BOTH, expand=YES)

# menu = Menu(root, tearoff=0)    # Creating a menubar
# main_menu = Menu(menu, tearoff=1)    # Creating a menu inside the menubar
# options_menu = Menu(menu, tearoff=1)    # Creating a menu inside the menubar

# main_menu.add_command(label="Print 'Hello World'", command=print_hello)
# main_menu.add_command(label="Print 'Bye'", command=print_bye)

# options_menu.add_command(label="Print 'Hello World'", command=print_hello)
# options_menu.add_command(label="Print 'Bye'", command=print_bye)

# menu.add_cascade(label="Main", menu=main_menu)    # Adding cascade
# menu.add_cascade(label="Options", menu=options_menu)    # Adding cascade

# root.config(menu=menu)    # So that the menubar is visible
