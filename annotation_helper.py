import shapely.geometry as geo # Polygon, Point
import geojson
import numpy as np
from shapely.plotting import plot_polygon
from dcis_utils import print_function_dec


class Annotation():
    """This represents a QuPath Annotation and its Properties"""
    # It takes four parameters:
    # - 'name': a string representing the name of the annotation
    # - 'color': a string representing the color of the annotation
    # - 'pts': an np.array(len_of_points, 2)
    # - 'og_index': an integer representing the original index of the annotation
    def __init__(self, name: str, color: str, pts: np.array, og_index: int) -> None:
        self.name = name
        self.color = color
        self.points = pts
        self.original_index = og_index
        self.geo_polygon = geo.Polygon(pts)
    
    def __str__(self):
        return f'Annotation {self.name}, {self.original_index}, {self.color}, {self.points.shape}'


class AnnotationHelper():
    "This class is related to everything that has to do with annotations and geojson export file"
    def __init__(self, annotated_geojson_filepath, image_dims=(3700, 3700)) -> None:
        self.filepath = annotated_geojson_filepath
        self.img_dims = image_dims

        self.annotations = []
        self.feature_collection_dict = {}
        
        with open(annotated_geojson_filepath, "r") as exported_annotation_fp:
            self.feature_collection_dict = geojson.load(exported_annotation_fp)
            
        self._load_annotations() # Will Set self.annotations

    def _load_annotations(self):
        """  Gets Annotation Object in form of {colors, points} from exorted QuPath Annotations """
        for i, self.feature_collection_dict in enumerate(self.feature_collection_dict['features']):
           
            # Depending on how a human exported the annotations, the info like color or name
            # may be in the properities field or the props[classification] field
            points = self.feature_collection_dict['geometry']['coordinates'][0]
            if self.feature_collection_dict['properties'].get('classification', None):
                classification = self.feature_collection_dict['properties']['classification']
            else:
                classification = self.feature_collection_dict['properties']
            
            name = classification['name']  # Ex: DCIS, Ignore
            color = classification.get('color', [255, 0, 0]) # Ex: [255, 0, 255]
            
            self.annotations.append(Annotation( name, color, np.array(points), i))
    
    def get_annotation_indexes(self, annos_to_draw=[]):
        specific_annos = []
        for annotation in self.annotations:
            if(annotation.name in annos_to_draw or str(annotation.original_index) in annos_to_draw ):
                specific_annos.append(annotation.original_index)
        return specific_annos
    
    def get_annotations_from_indexes(self, anno_indexes):
        annos = []
        for anno in self.annotations:
            if(anno.original_index in anno_indexes or not anno_indexes):
                annos.append(anno)
        return annos

    def get_specific_annotations(self, anno_names=[]):
        """Create a new list full of annotations that fit the specific names"""
        if not anno_names:
            return self.annotations
        specific_annos = []
        for annotation in self.annotations:
            if(annotation.name in anno_names):
                specific_annos.append(annotation)
        return specific_annos
    
    def get_final_union_zones(self, zones, anno_indexes):
        """This takes each annotation, and creates the additional zones (+1 for other stromal) and sends it"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        for annotation in self.annotations:
            if(annotation.original_index in anno_indexes):
                original_annotation_poly = annotation.geo_polygon
                curr_poly = []
                for i, zone in enumerate(zones):                
                    if(zone <= 0):
                        difference_poly = original_annotation_poly
                    else:
                        poly_to_use = curr_poly[i - 1] # Previous Sized Polygon
                        zone_size = zone - zones[i - 1] # What to increase boundary by in pixels
                        dilated_poly = poly_to_use.buffer(zone_size, single_sided=True) # Increase Boundaries
                        difference_poly = picture_poly.intersection(dilated_poly) #If boundaries extend outside of image, cut it out
                        # difference_poly = dilated_poly.difference(poly_to_use) #.difference(original_annotation_poly)      
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
    
    def get_final_zones(self, zones, annotations_names=[]):
        """This takes each annotation, and creates the additional zones (+1 for other stromal) and sends it"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        for annotation in self.annotations:
            if(not annotations_names or annotation.name in annotations_names):
                original_annotation_poly = annotation.geo_polygon
                curr_poly = []
                for i, zone in enumerate(zones):                
                    if(zone <= 0):
                        difference_poly = original_annotation_poly
                    else:
                        poly_to_use = curr_poly[i - 1] # Previous Sized Polygon
                        zone_size = zone - zones[i - 1] # What to increase boundary by in pixels
                        dilated_poly = poly_to_use.buffer(zone_size, single_sided=True) # Increase Boundaries
                        difference_poly = picture_poly.intersection(dilated_poly) #If boundaries extend outside of image, cut it out
                        # difference_poly = dilated_poly.difference(poly_to_use) #.difference(original_annotation_poly)      
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
    
    def get_zones_per_annotation(self, zones, anno_index):
        list_of_union_zones = [None] * len(zones)
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        original_annotation_poly = self.annotations[anno_index].geo_polygon
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
                poly_to_use = curr_poly[i - 1] # Previous Sized Polygon
                zone_size = zone - zones[i - 1] # What to increase boundary by in pixels
                dilated_poly = poly_to_use.buffer(zone_size, single_sided=True) # Increase Boundaries
                difference_poly = picture_poly.intersection(dilated_poly) #If boundaries extend outside of image, cut it out
                # difference_poly = dilated_poly.difference(poly_to_use) #.difference(original_annotation_poly)      # CHECK
            if(list_of_union_zones[i]):
                list_of_union_zones[i] = list_of_union_zones[i].union(difference_poly)
            else:
                list_of_union_zones[i] = difference_poly
            curr_poly.append(difference_poly)
        other_stromal_area =  geo.Polygon([[p[0], p[1]] for p in point_list])
        other_stromal_area = other_stromal_area.difference(curr_poly[-1])
        
          # This piece deals with all overlapping sections in the 
        final_to_add = list_of_union_zones[0]
        for i, zone in enumerate(list_of_union_zones[1:]):
            zone = zone.difference(final_to_add)
            list_of_union_zones[i+1] = zone
            final_to_add = final_to_add.union(zone)
        
        return list_of_union_zones + [other_stromal_area]
    
    def get_zones_per_anno_index(self, zones, anno_indexes):
        """This takes each annotation, and creates the additional zones (+1 for other stromal) and sends it"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        for annotation in self.annotations:
            if( annotation.original_index in anno_indexes):
                original_annotation_poly = annotation.geo_polygon
                curr_poly = []
                for i, zone in enumerate(zones):                
                    if(zone <= 0):
                        difference_poly = original_annotation_poly
                    else:
                        poly_to_use = curr_poly[i - 1] # Previous Sized Polygon
                        zone_size = zone - zones[i - 1] # What to increase boundary by in pixels
                        dilated_poly = poly_to_use.buffer(zone_size, single_sided=True) # Increase Boundaries
                        difference_poly = picture_poly.intersection(dilated_poly) #If boundaries extend outside of image, cut it out
                        # difference_poly = dilated_poly.difference(poly_to_use) #.difference(original_annotation_poly)      
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
    
    def get_zones_for_single_anno(self, zones, anno_index):
        list_of_union_zones = [None] * len(zones)
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        
        original_annotation_poly = self.annotations[anno_index].geo_polygon
        for i, zone in enumerate(zones):                
            if(zone <= 0):
                difference_poly = original_annotation_poly
            else:
                poly_to_use = list_of_union_zones[i - 1] # Previous Sized Polygon
                zone_size = zone - zones[i - 1] # What to increase boundary by in pixels
                dilated_poly = poly_to_use.buffer(zone_size, single_sided=True) # Increase Boundaries
                difference_poly = picture_poly.intersection(dilated_poly) #If boundaries extend outside of image, cut it out
            list_of_union_zones[i] = difference_poly

        other_stromal_area =  geo.Polygon([[p[0], p[1]] for p in point_list])
        for final_union_zone_polygon in list_of_union_zones:
            other_stromal_area = other_stromal_area.difference(final_union_zone_polygon)
            
        return list_of_union_zones + [other_stromal_area]
    
    @print_function_dec
    def get_final_zones_for_plotting(self, zones, annotations_names=[]):
        """USED ONLY FOR PLOTTING. Ignore otherwise"""
        list_of_union_zones = [None] * len(zones)
        
        point_list = [[0,0], [self.img_dims[0], 0], [self.img_dims[0], self.img_dims[1]], [0, self.img_dims[1]]]
        picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
        
        for annotation in self.annotations:
            if(not annotations_names or annotation.name in annotations_names):
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
                        difference_poly = picture_poly.intersection(dilated_poly) # Getting rid of stuff past photo edges
                    if(list_of_union_zones[i]):
                        list_of_union_zones[i] = list_of_union_zones[i].union(difference_poly)
                    else:
                        list_of_union_zones[i] = difference_poly
                    curr_poly.append(difference_poly)
        
        # This Cleans up the Final Stromal Area
        other_stromal_area =  geo.Polygon([[p[0], p[1]] for p in point_list])
        for final_union_zone_polygon in list_of_union_zones:
            other_stromal_area = other_stromal_area.difference(final_union_zone_polygon)

        # This piece deals with all overlapping sections in the 
        final_to_add = list_of_union_zones[0]
        for i, zone in enumerate(list_of_union_zones[1:]):
            zone = zone.difference(final_to_add)
            list_of_union_zones[i+1] = zone
            final_to_add = final_to_add.union(zone)
            
        return list_of_union_zones + [other_stromal_area]
    
    def get_annotation_areas(self):
        """This function gets all of the annotations area for total, annos, and stromal with percentaes"""
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
    

#TODO: Double check the interactions of the zones brother
    



# print(f"Feature {colored(str(i), 'green')} - Type: {feature_collection_annotation['type']}, id:{feature_collection_annotation['id']}, Props:{feature_collection_annotation['properties']}")
# Type: Feature, id:3affff8b-be30-410f-ae1f-a415d831b074, Props:{'objectType': 'annotation', 'classification': {'name': 'Ignore', 'color': [255, 0, 0]}
# patches_polygons.append(patches.Polygon(np.array(points), closed=True))
# import matplotlib.patches as patches
        #         self.all_annotations = []
        # self.all_annotations.append(Annotation( name, color, np.array(points), i))
        # self.patch_polygons = [] self.patch_polygons.append(patches.Polygon(np.array(points), closed=True))
        #     def reset_annotations(self):
        # self.annotations = self.all_annotations
        
