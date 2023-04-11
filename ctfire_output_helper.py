from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
from numpyencoder import NumpyEncoder
import json
from termcolor import cprint, colored
from dcis_utils import print_function_dec

class CTFIREOutputHelper():
    def __init__(self, mat_filepath):
        """This helper is made to assist with getting the CTF output from the matfile. It expects the basic Mat File."""
        # These values should more or less never be changed
        self._ctfire_dict = loadmat(mat_filepath)
        self._ctf_params = self.ctfire_dict['ctfP']['value'][0][0] 
        self._curvelet_params = self.ctfire_dict['cP']
        self._length_threshold = self.curvelet_params['LL1'][0][0].flatten()[0]
        
        # NOTE: fiber lengths is the only aspect that we store EVERY one of. We need to do this for indexing reasons
        self._fiber_lengths = self.ctfire_dict['data']['M'][0][0]['L'][0][0].flatten()
        
        # NOTE: Storing THRESHOLDED in the following NOT All ones for fast polling
        self._fibers = self.get_fibers()
        self._fiber_widths = self.get_fiber_widths()
        self._fiber_angles = self.get_fiber_angles()

        # These require fibers to be passed in, but initial centroids and midpoints will be saved
        self._centroids = self.get_centroids(self.fibers)
        self._midpoints = self.get_midpoints(self.fibers)

    def __getitem__(self, key):
        return self._ctfire_dict[key]

    # Properties Never should change
    @property
    def ctfire_dict(self):
        return self._ctfire_dict    
    
    @property
    def ctf_params(self):
        return self._ctf_params    
    
    @property
    def curvelet_params(self):
        return self._curvelet_params
    
    @property
    def length_threshold(self):
        return self._length_threshold
    
    @property
    def fiber_lengths(self):
        return self._fiber_lengths
    
    def get_fiber_lengths(self, length_threshold=None):
        """Gets all fiber lengths less than threshold"""
        if length_threshold is None:
            length_threshold = self.length_threshold
        
        # Makes all values less than threshold zero
        lengths_greater_than_threshold = np.where(self.fiber_lengths > length_threshold, self.fiber_lengths, 0)
        final_lengths = lengths_greater_than_threshold[lengths_greater_than_threshold != 0] # Cuts out all zero values

        return final_lengths
    
    @property
    def fibers(self):
        return self._fibers
    
    def get_fibers(self, length_threshold=None):
        """Get all of the fibers (arr of coords (x,y)) that are less than the length of threshold

            Returns a list of fibers (arr of coords (x,y))
        """
        if length_threshold is None:
            length_threshold = self.length_threshold

        indexes_of_lengths_greater_than_threshold = np.where(self.fiber_lengths > length_threshold)[0]
        lengths_greater_than_threshold = np.where(self.fiber_lengths > length_threshold, self.fiber_lengths, 0)
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
        return all_coords

    @property
    def fiber_widths(self):
        return self._fiber_widths
    
    def get_fiber_widths(self, length_threshold=None):
        if length_threshold is None:
            length_threshold = self.length_threshold

        indexes_of_lengths_greater_than_threshold = np.where(self.fiber_lengths > length_threshold)[0]
        length_to_use = len(indexes_of_lengths_greater_than_threshold)
        widths = np.ones((length_to_use))
        for i in range(length_to_use):
            vertices_to_use = self.ctfire_dict['data']['Fa'][0][0][0][indexes_of_lengths_greater_than_threshold[i]]['v'][0]
            width = 2 * np.mean(self.ctfire_dict['data']['Ra'][0][0][vertices_to_use-1])
            widths[i] = width
        return widths
    
    @property
    def fiber_angles(self):
        return self._fiber_angles
    
    def get_fiber_angles(self, length_threshold=None):
        if length_threshold is None:
            length_threshold = self.length_threshold

        angle_indexes = np.where(self.fiber_lengths  > length_threshold)[0]
        angles = self.ctfire_dict['data']['M'][0][0]['angle_xy'][0][0].flatten()
        
        return angles[angle_indexes]

    def _centeroidnp(self, x_points, y_points):
        length = x_points.shape[0]
        sum_x = np.sum(x_points)
        sum_y = np.sum(y_points)
        return sum_x / length, sum_y / length

    @property
    def centroids(self):
        return self._centroids
    
    def get_centroids(self, fibers):
        all_centroids = np.zeros((len(fibers), 2), dtype='int16')
        for i in range(len(all_centroids)):
            x_points = fibers[i][:, 0]
            y_points = fibers[i][:, 1]
            centroid = self._centeroidnp(x_points, y_points)
            all_centroids[i] = centroid
        return all_centroids

    @property
    def midpoints(self):
        return self._midpoints
    
    def get_midpoints(self, fibers):
        all_middles = np.zeros((len(fibers), 2), dtype='int16')
        for i in range(len(fibers)):
            middle_point = np.median(fibers[i], axis=0)
            all_middles[i] = middle_point
        return all_middles


if __name__ == '__main__':
    pass
  