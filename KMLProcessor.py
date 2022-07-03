import re

import numpy as np
from matplotlib import pyplot as plt
import geopy.distance
from pykml import parser


def get_coordinates_from_kml_file(file_path):
    with open(file_path,'rb') as f :
        doc = parser.parse(f)
        for t in doc.getiterator():
            if "coordinates" in t.tag:
                waypoints = []
                ext = t.text.strip()
                for csv in re.split(r'\s', ext):
                    longitude,latitude, altitude  = csv.split(',')
                    waypoints.append([longitude,latitude, altitude ])
    arr = np.array(waypoints)
    arr_f = np.delete(arr, -1, axis=1).astype("float")
    
    return arr_f
    
    
def get_distances(coordinates):
    d = [geopy.distance.geodesic(coordinates[i], coordinates[i + 1]).km if i < len(coordinates) - 1 else 0 for i, x in enumerate(coordinates)]
    d = np.array(d)
    print(d)
    return d


def filter_distance_using_average(d):
    d_s = d[d > 0]
    f_d = d_s.copy()
    mean = d_s.mean()
    std = d_s.std()
    f_d[f_d > mean] = 0

    if __name__ == '__main__':
        fig = plt.figure()
        plt.plot(d_s,label="original signal")
        plt.plot(f_d, label="Filtered signal")
        plt.plot([mean] * len(d_s),label="Average")
        plt.plot([abs(f_d).std()] * len(d_s),label="Standard Deviation")
        plt.title(f'Distances Signal filter using Average step Size')
        plt.ylabel('Distance in km')
        plt.xlabel('Indexes')
        plt.legend(loc='upper left')
        # plt.show()
    print(sum(f_d))

    threshold_list = [mean] * len(d_s)
    return f_d,d_s,threshold_list


def filter_distance_using_diff(d):

    d_s = d[d > 0]
    d_sf = np.diff(d_s)
    d_ss = d_s.copy()

    mean_2 = abs(d_sf).mean()
    std_2 = abs(d_sf).std()
    var_2 = abs(d_sf).var()

    i = 0
    while i < len(d_sf):
        if abs(d_sf[i]) > mean_2:
            if d_sf[i - 1] > mean_2:
                d_ss[i] = np.average(d_ss[i - 2:i])
                d_ss[i + 1] = np.average(d_ss[i - 1:i + 1])
                d_ss[i + 2] = np.average(d_ss[i:i + 2])
                d_ss[i + 3] = np.average(d_ss[i + 1:i + 3])
                print("In")
            else:
                d_ss[i + 1] = np.average(d_ss[i - 1:i + 1])
                d_ss[i + 2] = np.average(d_ss[i:i + 2])
            i += 3

        else:
            i += 1

    if __name__ == '__main__':
        fig2 = plt.figure()
        plt.plot(d_s,label="original signal")
        plt.plot(d_ss, label = "Filtered signal")
        plt.plot([max(d_ss)] * len(d_ss), label="Threshold")

        plt.title(f'Distances Signal filter using Differentiation')
        plt.ylabel('Distance in km')
        plt.xlabel('Indexes')
        plt.legend(loc='upper left')

        plt.show()
    print(sum(d_ss))

    threshold_list = [max(d_ss)] * len(d_ss)
    return d_ss,d_s ,threshold_list



def process_using_diff_method(path):
    cor = get_coordinates_from_kml_file(path)
    distances = get_distances(cor)
    f_d ,d,threshold = filter_distance_using_diff(distances)
    return list(f_d) ,list(d),threshold ,sum(f_d)

def process_using_average_method(path):
    cor = get_coordinates_from_kml_file(path)
    distances = get_distances(cor)
    f_d,d,threshold = filter_distance_using_average(distances)
    return list(f_d) ,list(d), threshold , sum(f_d)


if __name__ =="__main__":
    cor = get_coordinates_from_kml_file("./task_2_sensor.kml")
    distances = get_distances(cor)
    filter_distance_using_average(distances)
    filter_distance_using_diff(distances)



