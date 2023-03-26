import numpy as np
from termcolor import cprint, colored
# def mult()
# test_arr = np.array(range(15)).reshape((3,5))
# dists = np.ones((29))
# dists = dists[np.array(range(29))] * 
        # # poly_buckets = np.ones((len(annotation_helper_obj.geo_polygons))) * geo_polygon.exterior.distance(centroid_point) 
        # poly_buckets = np.fill((len(annotation_helper_obj.geo_polygons))) * geo_polygon.exterior.distance(centroid_point) 
        # # poly_buckets = poly_buckets.fill(np.array((len(annotation_helper_obj.geo_polygons))) * geo_polygon.exterior.distance(centroid_point))
        # temp = np.array([AnnotationHelper()])
        
# Notes:
# arr.ndim
# arr.shape Ex:
# arr.dtype

# Get test arr

# Would also like to calculate the collagen signal density in total stromal region and in specific stromal zones defined by distance
# from the epithelial mask. Easy to use ImageJ for this but unsure if could do this analysis in the the zones.

fiber_buckets_simulation = np.array([
    [1, 0, 1], #Fiber
    [1, 2, 2], #Fiber
    [0, 2, 3], #Fiber
    [0, 3, 3], #Fiber
    [3, 3, 3], #Fiber
    #Each col is bucketed
])

fibers_simulation = np.array([
    [1, 1, 1, 1],
    [2, 2, 2, 2],
    [3,3,3,3],
    [4,4,4,4],
    [5,5,5,5],
])

widths_simulation = np.array([4,5,6,7,8])
length_simulation = np.array([1,2,3,4,5])

x_simul = np.array([1,2,3,4,5])
y_simul = np.array([1,2,3,4,5])

print(np.vstack((x_simul, y_simul)).T)
temp_test = np.array([0,2,3])
temp_test2 = np.array([0, 10, 11, 4, 5, 12])

# print(np.arange(4))
# print(fibers_simulation[temp_test])
# print(np.where(temp_test2 > 10)[0])
# print(np.min(fiber_buckets_simulation, axis=0)) # Per Annotation # Do not use, just use the index
# print(np.min(fiber_buckets_simulation, axis=1)) # Per Fiber
# print(fiber_buckets_simulation[:, 1])
# fibs_in_annos = np.where(fiber_buckets_simulation[:, 1] == 2)
# print(widths_simulation[fibs_in_annos])

# print(widths_simulation * length_simulation)

# labeled_fibers = fiber_buckets_simulation.min(axis=1)
# cprint(f"Labeled Fibers: {labeled_fibers}", 'green')
# sum_values = np.array(range(4))
# cprint(f"sum_values: {sum_values}", 'cyan')
# final_counts = {0:0, 1:0, 2:0, 3:0}
# for i, fiber in enumerate(fibers_simulation):
#     final_counts[labeled_fibers[i]] += 1
# print(final_counts)
# print(np.sum(fibers_simulation[sum_values], axis=0))

# fiber_per_annotation = fiber_buckets_simulation[:, 2:].flatten()
# print(fiber_per_annotation)
# for i, bucket in enumerate(fiber_per_annotation):
#     final_counts[bucket] += widths_simulation[i] * length_simulation[i]
# print(final_counts)
# print(np.where(labeled_fibers == 0))

# temp = np.array((4,2))
# print(np.unique(widths_simulation2))

# for i in range(4):
#     if(widths.any()):
#         cprint(f"{i, np.mean(widths), widths}", 'magenta')
# FINAL ANSWER SHOULD BE: [12, 4, 0, 4]


# calculate_singal_density_of_all_stroma(test, test2)
# print(sub_array)
# final_test = np.where(np.any(test == [0], axis=0))
# print("TEST ", final_test)
# a = np.zeros((1,4,2))
# b = np.array([1, 2, 3])
# c = np.array([5, 6, 7])
# d = b + 2
# e = c*2

# l = [1,2,3]
# l2 = [4,5,6]
# print(list(zip(l, l2)))
#
# coords = np.stack((b,c), axis=1)
# coords2 = np.stack((d,e), axis=1)
# coords3 = np.array([[1,2], [11,12]])
# final = coords
# # final = np.stack((final, coords3))
# final = np.append(final,coords3,axis=0)
# print(coords)
#
# print(coords[:,0])
# print(coords.flatten())
# test = np.array([[[1,2]], [[1,2], [2,3]]])

# test2 = np.zeros((6,2))
# test2[0:coords.size[0]] = coords
# print(test2)
# a[0] = coords
# print(a)
# print(np.concatenate((a, coords)))
# print(a)
# a = np.array([[1,2,3],[4,5,6],[7,8,9], [10,11,12], [13,14,15]])
# b = a[[0, 1]]
# cancer = data.Xa(vertices_to_use,:)


# print(np.ones((10)))
# print(np.ones((10,)))
# print(np.ones((10,1)))
