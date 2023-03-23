import shapely.geometry as geo # Polygon, Point
import matplotlib.patches as patches
import geojson
import numpy as np
from shapely.plotting import plot_polygon

class Annotation():
    def __init__(self, name, color, pts) -> None:
        self.name = name
        self.color = color
        self.points = pts
        self.geo_polygon = geo.Polygon(pts)

class AnnotationHelper():
    "This class is related to everything that has to do with annotations and geojson export file"
    def __init__(self, annotated_geojson_filepath, image_dims=(3700, 3700)) -> None:
        # self.patch_polygons = [] self.patch_polygons.append(patches.Polygon(np.array(points), closed=True))
        self.filepath = '' # geojson filepath
        self.img_dims = image_dims
        
        self.feature_collection_dict = {}
        self.annotations = []
        self.zoned_polys = []
        
        with open(annotated_geojson_filepath, "r") as exported_annotation_fp:
            self.feature_collection_dict = geojson.load(exported_annotation_fp)
        self._load_annotations()

    def _load_annotations(self):
        """Gets Annotation Object in form of {colors, points} from exorted QuPath Annotations"""
        for i, self.feature_collection_dict in enumerate(self.feature_collection_dict['features']):
                # print(f"Feature {colored(str(i), 'green')} - Type: {feature_collection_annotation['type']}, id:{feature_collection_annotation['id']}, Props:{feature_collection_annotation['properties']}")
                # Type: Feature, id:3affff8b-be30-410f-ae1f-a415d831b074, Props:{'objectType': 'annotation', 'classification': {'name': 'Ignore', 'color': [255, 0, 0]}
                points = self.feature_collection_dict['geometry']['coordinates'][0]
                if self.feature_collection_dict['properties'].get('classification', None):
                    classification = self.feature_collection_dict['properties']['classification']
                else:
                    classification = self.feature_collection_dict['properties']
                
                name = classification['name']  # Ex: DCIS, Ignore
                color = classification.get('color', [255, 0, 0]) # Ex: [255, 0, 255]
                
                self.annotations.append(Annotation( name, color, np.array(points)))

    def get_annoatations(self):
        return self.annotations
    
    def get_final_zones(self, zones):
        """This takes each annotation, and creates the additional zones (+1 for other stromal) and sends it"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        
        for annotation in self.annotations:
            original_annotation_poly = annotation.geo_polygon
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
    
    def get_final_zones_for_plotting(self, zones, ax):
        """USED ONLY FOR PLOTTING. Ignore otherwise"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        
        for annotation in self.annotations:
            original_annotation_poly = annotation.geo_polygon
            # Fixes y to adjust to 0,0 in bottom left for plot (not 0,0 top left for image)
            curr_poly = []
            x, y = original_annotation_poly.exterior.xy
            img_height = self.img_dims[1]
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
    
    def get_annotation_areas(self):
        annotation_area = 0
        total_area = self.img_dims[0] * self.img_dims[1]
        for annotation in self.annotations:
            annotation_area += annotation.geo_polygon.area
            
        stromal_area = self.img_dims[0] * self.img_dims[1] - annotation_area
        stromal_percentage = stromal_area / total_area
        annotation_percentage = annotation_area / total_area

        return total_area, stromal_area, annotation_area, stromal_percentage, annotation_percentage

    def __getitem__(self, key):
        return self.feature_collection_dict[key]
    
    
    # patches_polygons.append(patches.Polygon(np.array(points), closed=True))