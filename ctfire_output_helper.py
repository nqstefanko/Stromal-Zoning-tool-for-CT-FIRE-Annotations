from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
from numpyencoder import NumpyEncoder
import json
from termcolor import cprint, colored
# mat_filepath = r"C:\Users\nqste\Code\UCSF\DCIS\DCIS_Collagen_Collaboration\ctFIRE_v2.0Beta_TestImages\ctFIREout\ctFIREout_2B_D9_crop2.mat"


class CTFIREOutputHelper():
    def __init__(self, mat_filepath):
        self.ctfire_dict = loadmat(mat_filepath)
        self.fibers = None
        self.fiber_lengths = None
        self.length_threshold = None
        self.centroids = None
        self.fiber_widths = None
        self.fiber_angles = None

    def get_ctfire_params(self):
        return self.ctfire_dict['ctfP']['value'][0][0]  # ['thresh_dang_L'][0][0].flatten()

    def get_curvelet_params(self):
        return self.ctfire_dict['cP']

    def get_fiber_lengths_thresholded(self):
        length_threshold = self.get_fiber_len_threshold()
        length_of_fibers = self.ctfire_dict['data']['M'][0][0]['L'][0][0].flatten()

        lengths_greater_than_threshold = np.where(length_of_fibers > length_threshold, length_of_fibers, 0)
        lengths_greater_than_threshold = lengths_greater_than_threshold[lengths_greater_than_threshold != 0]

        self.fiber_lengths = lengths_greater_than_threshold
        return self.fiber_lengths
        
    def get_fiber_lengths(self):
        self.fiber_lengths = self.ctfire_dict['data']['M'][0][0]['L'][0][0].flatten()
        return self.fiber_lengths

    def get_fiber_len_threshold(self):
        if(self.length_threshold is None):
            ctfire_params = self.get_curvelet_params()
            self.length_threshold = ctfire_params['LL1'][0][0].flatten()[0]
        return self.length_threshold

    def get_fiber_vertices_thresholded(self):
        length_threshold = self.get_fiber_len_threshold()
        length_of_fibers = self.get_fiber_lengths()

        indexes_of_lengths_greater_than_threshold = np.where(length_of_fibers > length_threshold)[0]
        lengths_greater_than_threshold = np.where(length_of_fibers > length_threshold, length_of_fibers, 0)
        lengths_greater_than_threshold = lengths_greater_than_threshold[lengths_greater_than_threshold != 0]

        assert len(indexes_of_lengths_greater_than_threshold) == len(lengths_greater_than_threshold)

        all_coords = []
        for i in range(len(lengths_greater_than_threshold)):
            vertices_to_use = self.ctfire_dict['data']['Fa'][0][0][0][indexes_of_lengths_greater_than_threshold[i]]['v'][0]
            xa_data = self.ctfire_dict['data']['Xa'][0][0]
            xy_points = xa_data[vertices_to_use - 1]

            x_points = xy_points[:, 0].astype('int16')
            y_points = xy_points[:, 1].astype('int16')

            coords = np.stack((x_points, y_points), axis=1)
            all_coords.append(coords)
        self.fibers = all_coords

        return self.fibers

    def get_fiber_vertices(self):
        all_coords = []
        for i in range(len(self.get_fiber_lengths())):
            vertices_to_use = self.ctfire_dict['data']['Fa'][0][0][0][i]['v'][0]
            xa_data = self.ctfire_dict['data']['Xa'][0][0]
            xy_points = xa_data[vertices_to_use - 1]

            x_points = xy_points[:, 0].astype('int16')
            y_points = xy_points[:, 1].astype('int16')

            coords = np.stack((x_points, y_points), axis=1)
            all_coords.append(coords)
        self.fibers = all_coords
        return self.fibers

    def centeroidnp(self, x_points, y_points):
        length = x_points.shape[0]
        sum_x = np.sum(x_points)
        sum_y = np.sum(y_points)
        return sum_x / length, sum_y / length

    def get_centroids(self):
        if(self.fibers == None):
            cprint(f"No fibers available yet! Run get_fiber_vertices", "red")
            return None
        else:
            all_centroids = np.zeros((len(self.fibers), 2), dtype='int16')
            for i in range(len(all_centroids)):
                x_points = self.fibers[i][:, 0]
                y_points = self.fibers[i][:, 1]
                centroid = self.centeroidnp(x_points, y_points)
                all_centroids[i] = centroid
            self.centroids = all_centroids
        return self.centroids

    def get_midpoints(self):
        all_middles = np.zeros((len(self.fibers), 2), dtype='int16')
        for i in range(len(self.fibers)):
            middle_point = np.median(self.fibers[i], axis=0)
            all_middles[i] = middle_point
        return all_middles

    def get_fiber_widths_from_csv(self, csv_file):
        my_data = np.genfromtxt(csv_file, delimiter=',')
        print(my_data.shape)

    def get_fiber_widths_thresholded(self):
        length_threshold = self.get_fiber_len_threshold()
        length_of_fibers = self.get_fiber_lengths()

        indexes_of_lengths_greater_than_threshold = np.where(length_of_fibers > length_threshold)[0]
        length_to_use = len(indexes_of_lengths_greater_than_threshold)
        widths = np.ones((length_to_use))
        for i in range(length_to_use):
            vertices_to_use = self.ctfire_dict['data']['Fa'][0][0][0][indexes_of_lengths_greater_than_threshold[i]]['v'][0]
            width = 2 * np.mean(self.ctfire_dict['data']['Ra'][0][0][vertices_to_use-1])
            widths[i] = width
        self.fiber_widths = widths
        return self.fiber_widths
    
    def get_fiber_widths(self):
        length_of_fibers = self.get_fiber_lengths()
        length_to_use = len(length_of_fibers)
        widths = np.ones((length_to_use))
        for i in range(length_to_use):
            vertices_to_use = self.ctfire_dict['data']['Fa'][0][0][0][i]['v'][0]
            width = 2 * np.mean(self.ctfire_dict['data']['Ra'][0][0][vertices_to_use-1])
            widths[i] = width
        self.fiber_widths = widths
        return self.fiber_widths

    def get_fiber_angles(self):
        return self.ctfire_dict['data']['M'][0][0]['angle_xy'][0][0].flatten()

    def get_fiber_angles_thresholded(self):
        length_threshold = self.get_fiber_len_threshold()
        length_of_fibers = self.get_fiber_lengths()
        
        angle_indexes = np.where(length_of_fibers > length_threshold)[0]
        angles = self.ctfire_dict['data']['M'][0][0]['angle_xy'][0][0].flatten()
        
        self.fiber_angles = angles[angle_indexes]
        return self.fiber_angles

    def __getitem__(self, key):
        return self.ctfire_dict[key]


# ctfire_parameters = ctfire_export_dict['cP']
# ctfire_data = ctfire_export_dict['data']
# ctfire_M_data = ctfire_data['M']

# mat_dict = get_ctfire_output_dict_from_matfile(mat_filepath)
# print(mat_dict.keys())

# with open('dcis_data/all_coords_16.json', 'w') as f:
#     json.dump(all_coords, f, cls=NumpyEncoder)