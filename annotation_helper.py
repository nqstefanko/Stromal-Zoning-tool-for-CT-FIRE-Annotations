import shapely.geometry as geo # Polygon, Point
import matplotlib.patches as patches
import geojson
import numpy as np
from shapely.plotting import plot_polygon

class AnnotationHelper():
    def __init__(self) -> None:
        self.points = []
        self.geo_polygons = []
        self.patch_polygons = []
        self.annotation_info = []
        self.feature_collection_dict = {}
        self.filepath = ''
        self.zoned_polys = []

    def load_geojson_file(self, annotated_geojson_filepath):
        self.filepath = annotated_geojson_filepath
        with open(annotated_geojson_filepath, "r") as exported_annotation_fp:
            self.feature_collection_dict = geojson.load(exported_annotation_fp)
        return self.feature_collection_dict
    
    def get_annotations(self, annotated_geojson_filepath):
        """Gets Annotation Object in form of {colors, points} from exorted QuPath Annotations"""
        self.filepath = annotated_geojson_filepath

        with open(annotated_geojson_filepath, "r") as exported_annotation_fp:
            feature_collection_of_annotations = geojson.load(exported_annotation_fp)
            # self.geo_polygons = np.array(range(len(feature_collection_of_annotations['features'])))
            # print(self.geo_polygons.shape)
            for i, feature_collection_annotation in enumerate(feature_collection_of_annotations['features']):
                    # print(f"Feature {colored(str(i), 'green')} - Type: {feature_collection_annotation['type']}, id:{feature_collection_annotation['id']}, Props:{feature_collection_annotation['properties']}")
                    points = feature_collection_annotation['geometry']['coordinates'][0]
                    color = feature_collection_annotation['properties']['classification']['color'] # Ex: [255, 0, 255]
                    name = feature_collection_annotation['properties']['classification']['name']  # Ex: DCIS, Ignore
                    # Type: Feature, id:3affff8b-be30-410f-ae1f-a415d831b074, Props:{'objectType': 'annotation', 'classification': {'name': 'Ignore', 'color': [255, 0, 0]}
                    
                    self.points.append(np.array(points))
                    self.geo_polygons.append(geo.Polygon(points))
                    self.patch_polygons.append(patches.Polygon(np.array(points), closed=True))
                    self.annotation_info.append({'color': color, "name": name})
        return self.annotation_info, self.points, self.geo_polygons

    def get_final_zones(self, zones, img_dimensions=(3700, 3700)):
        """This takes each annotation, and creates the additional zones (+1 for other stromal) and sends it"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [img_dimensions[0], 0], [img_dimensions[0], img_dimensions[1]], [0, img_dimensions[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        
        for original_annotation_poly in self.geo_polygons:
            curr_poly = []
            for i, zone in enumerate(zones):                
                if(zone <= 0):
                    difference_poly = original_annotation_poly
                else:
                    poly_to_use = curr_poly[i - 1]
                    zone_size = zone - zones[i - 1]
                    dilated_poly = poly_to_use.buffer(zone_size, single_sided=True)
                    dilated_poly = picture_poly.intersection(dilated_poly)
                    difference_poly = dilated_poly.difference(poly_to_use).difference(original_annotation_poly)      
                
                if(list_of_union_zones[i]):
                    list_of_union_zones[i] = list_of_union_zones[i].union(difference_poly)
                else:
                    list_of_union_zones[i] = difference_poly
                curr_poly.append(difference_poly)

        other_stromal_area =  geo.Polygon([[p[0], p[1]] for p in point_list])
        for final_union_zone_polygon in list_of_union_zones:
            other_stromal_area = other_stromal_area.difference(final_union_zone_polygon)

        
        final_to_add = list_of_union_zones[0]
        for i, zone in enumerate(list_of_union_zones[1:]):
            zone = zone.difference(final_to_add)
            list_of_union_zones[i+1] = zone
            final_to_add = final_to_add.union(zone)
            
        return list_of_union_zones + [other_stromal_area]
    
    def get_final_zones_for_plotting(self, zones, ax,  img_dimensions=(3700, 3700)):
        """USED ONLY FOR PLOTTING. Ignore otherwise"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [img_dimensions[0], 0], [img_dimensions[0], img_dimensions[1]], [0, img_dimensions[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        
        for original_annotation_poly in self.geo_polygons:
            # Fixes y to adjust to 0,0 in bottom left for plot (not 0,0 top left for image)
            curr_poly = []
            x, y = original_annotation_poly.exterior.xy
            img_height = img_dimensions[1]
            y_points = np.abs(np.array(y) - img_height) 
            stacked = np.column_stack((x, y_points))
            fixed_y_annotation_poly = geo.Polygon(stacked)

            for i, zone in enumerate(zones):                
                if(zone <= 0):
                    difference_poly = fixed_y_annotation_poly
                else:
                    poly_to_use = curr_poly[i - 1]
                    zone_size = zone - zones[i - 1]
                    dilated_poly = poly_to_use.buffer(zone_size, single_sided=True)
                    dilated_poly = picture_poly.intersection(dilated_poly) # Getting rid of stuff past photo edges
                    difference_poly = dilated_poly.difference(poly_to_use).difference(fixed_y_annotation_poly)      
                
                if(list_of_union_zones[i]):
                    list_of_union_zones[i] = list_of_union_zones[i].union(difference_poly)
                else:
                    list_of_union_zones[i] = difference_poly
                curr_poly.append(difference_poly)

        # list_of_union_zones = reversed(list_of_union_zones)                    
        # list_of_union_zones.reverse()
        other_stromal_area =  geo.Polygon([[p[0], p[1]] for p in point_list])
        for final_union_zone_polygon in list_of_union_zones:
            other_stromal_area = other_stromal_area.difference(final_union_zone_polygon)

        final_to_add = list_of_union_zones[0]
        for i, zone in enumerate(list_of_union_zones[1:]):
            zone = zone.difference(final_to_add)
            list_of_union_zones[i+1] = zone
            final_to_add = final_to_add.union(zone)

            
        return list_of_union_zones + [other_stromal_area]
    
    def get_annotation_areas(self, img_dimensions=[3700, 3700]):
        annotation_area = 0
        total_area = img_dimensions[0] * img_dimensions[1]
        for g_poly in self.geo_polygons:
            annotation_area += g_poly.area
            
        stromal_area = img_dimensions[0] * img_dimensions[1] - annotation_area
        stromal_percentage = stromal_area / total_area
        annotation_percentage = annotation_area / total_area

        return total_area, stromal_area, annotation_area, stromal_percentage, annotation_percentage

    def __getitem__(self, key):
        return self.feature_collection_dict[key]
    
    
    # patches_polygons.append(patches.Polygon(np.array(points), closed=True))