import shapely.geometry as geo # Polygon, Point
import matplotlib.patches as patches
import geojson
import numpy as np

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
                # if(i == 26):
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
        list_of_union_zones = [None] * len(zones)
        self.zoned_polys = [[]] * len(self.geo_polygons)
        for i, original_annotation_poly in enumerate(self.geo_polygons):

            point_list = [[0,0], [img_dimensions[0], 0], [img_dimensions[0], img_dimensions[1]], [0, img_dimensions[1]]]
            picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
            
            # Fixes y to adjust to 0,0 in bottom left for plot (not 0,0 top left for image)
            for j, zone in enumerate(zones):
                if(zone <= 0):
                    difference_poly = original_annotation_poly
                else:
                    dilated_poly = original_annotation_poly.buffer(zone, single_sided=True)
                    dilated_poly = picture_poly.intersection(dilated_poly)
                    difference_poly = dilated_poly.difference(original_annotation_poly)        
                if(list_of_union_zones[j]):
                    list_of_union_zones[j] = list_of_union_zones[j].union(difference_poly)
                else:
                    list_of_union_zones[j] = difference_poly
                self.zoned_polys[i].append([difference_poly])

        list_of_union_zones.reverse()

        other_stromal_area =  geo.Polygon([[p[0], p[1]] for p in point_list])
        for final_union_zone_polygon in list_of_union_zones:
            other_stromal_area = other_stromal_area.difference(final_union_zone_polygon)

        return list_of_union_zones + [other_stromal_area]

    def get_final_zones_for_plotting(self, zones,  img_dimensions=(3700, 3700)):
        """USED ONLY FOR PLOTTING. Ignore otherwise"""
        list_of_union_zones = [None] * len(zones)
        for original_annotation_poly in self.geo_polygons:

            point_list = [[0,0], [img_dimensions[0], 0], [img_dimensions[0], img_dimensions[1]], [0, img_dimensions[1]]]
            picture_poly = geo.Polygon([[p[0], p[1]] for p in point_list])
            x, y = original_annotation_poly.exterior.xy
            
            # Fixes y to adjust to 0,0 in bottom left for plot (not 0,0 top left for image)
            img_height = img_dimensions[1]
            y_points = np.abs(np.array(y) - img_height) 
            stacked = np.column_stack((x, y_points))
            fixed_y_annotation_poly = geo.Polygon(stacked)
            for i, zone in enumerate(zones):
                if(zone <= 0):
                    difference_poly = fixed_y_annotation_poly
                else:
                    dilated_poly = fixed_y_annotation_poly.buffer(zone, single_sided=True)
                    dilated_poly = picture_poly.intersection(dilated_poly)
                    difference_poly = dilated_poly.difference(fixed_y_annotation_poly)        
                if(list_of_union_zones[i]):
                    list_of_union_zones[i] = list_of_union_zones[i].union(difference_poly)
                else:
                    list_of_union_zones[i] = difference_poly
                    
        list_of_union_zones.reverse()
        other_stromal_area =  geo.Polygon([[p[0], p[1]] for p in point_list])
        for final_union_zone_polygon in list_of_union_zones:
            other_stromal_area = other_stromal_area.difference(final_union_zone_polygon)

        return list_of_union_zones + [other_stromal_area]

    # def create_zoned_polys(self, zones):
    #     for poly in self.geo_polygons:
    #         final_zones = {}
    #         for zone in zones:
    #             x, y = poly.exterior.xy
    #             final_zones[zone] = poly.buffer(zone, single_sided=True)
    #         self.zoned_polys.append(final_zones)
    #     return self.zoned_polys


    def __getitem__(self, key):
        return self.feature_collection_dict[key]
    
    
    # patches_polygons.append(patches.Polygon(np.array(points), closed=True))