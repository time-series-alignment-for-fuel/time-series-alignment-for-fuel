from data_loader import DataLoader
import os
import time
import numpy as np
from PIL import Image
import kdtree
import math

ROOT_PATH = "../enrichData-30/"
TRUTH_PATH = "../alignData/"
INITIAL_PATH = "./initialData/"
MAP_PATH = "./initialMapConstraint/"
ALIGNMENT_DATA_PATH = "./enrichmentData/"
PARAMETER_RESULT_PATH = "./exp6-4-1/"


class Alignment(object):

    def __init__(self):
        self.raw_data = None
        self.X = []
        self.Y = []
        self.Z = []
        self.mapID = 0
        self.delta = 50
        self.map = []

    def preprocessing(self, path, length=0):
        dataloader = DataLoader()
        self.raw_data = None
        self.X = []
        self.Y = []
        self.Z = []
        self.raw_data = dataloader.get_data(path)
        if length != 0:
            self.raw_data = self.raw_data[1:3*length+1]
        else:
            self.raw_data = self.raw_data[1:]
        for r in self.raw_data:
            ts = self.time2ts(r[1])
            if r[2] != "":
                self.X.append([ts,float(r[2])])
            elif r[3] != "":
                self.Y.append([ts, float(r[3])])
            elif r[4] != "":
                self.Z.append([ts, float(r[4])])

    def initialization(self, w):
        candidate_list = self.time_constraint(w)
        result_list = []
        # greedy initialization
        time_set = set()
        for c in candidate_list:
            if c[0] not in time_set and c[1] not in time_set and c[2] not in time_set:
                time_set.add(c[0])
                time_set.add(c[1])
                time_set.add(c[2])
                result_list.append(c)
        return result_list

    def time_constraint(self, w):
        candidate_list = []
        y_1 = 0
        y_2 = 0
        z_1 = 0
        z_2 = 0
        for i in range(len(self.X)):
            x = self.X[i]
            ts = x[0]
            while y_1 < len(self.Y) and self.Y[y_1][0] < ts - w:
                y_1 += 1
            while z_1 < len(self.Z) and self.Z[z_1][0] < ts - w:
                z_1 += 1
            while y_2 < len(self.Y) and self.Y[y_2][0] < ts + w:
                y_2 += 1
            while z_2 < len(self.Z) and self.Z[z_2][0] < ts + w:
                z_2 += 1
            if y_1 >= len(self.Y) or z_1 >= len(self.Z):
                break
            for j in range(y_1, y_2):
                for k in range(z_1, z_2):
                    if -w < self.Y[j][0] - self.Z[k][0] < w:
                        candidate_list.append([x[0], self.Y[j][0], self.Z[k][0], x[1], self.Y[j][1], self.Z[k][1]])
        return candidate_list

    def time_constraint_opt(self, w):
        # ground truth, use for test
        candidate_list = []
        for i in range(min(len(self.X), len(self.Y), len(self.Z))):
            t1 = self.X[i][0]
            t2 = self.Y[i][0]
            t3 = self.Z[i][0]
            if abs(t1-t2) + abs(t2-t3) + abs(t1-t3) < 2*w:
                candidate_list.append([self.X[i][0], self.Y[i][0], self.Z[i][0], self.X[i][1], self.Y[i][1], self.Z[i][1]])
        return candidate_list

    def time2ts(self, s):
        timeArray = time.strptime(s, "%Y-%m-%d %H:%M:%S")
        try:
            ts = int(time.mktime(timeArray))
        except:
            print(s)
        return ts

    def alignment(self, w, opt=False, ignore_delta=False, kd=False):
        # w: window size
        # f: map constraint
        candidate_list = []
        if opt:
            candidate_list = self.time_constraint_opt(w)
        else:
            candidate_list = self.time_constraint(w)
        if not ignore_delta:
            # perform map constarint
            if kd:
                candidate_list = [c for c in candidate_list if self.map_constraint_kd(c)]
            else:
                candidate_list = [c for c in candidate_list if self.map_constraint(c)]

        # construct intersect dictionary
        time_dict = {}
        intersect_dict = {}
        for idx, c in enumerate(candidate_list):
            t1 = c[0]
            t2 = c[1]
            t3 = c[2]
            self.add_dict_a_with_b(time_dict, t1, idx)
            self.add_dict_a_with_b(time_dict, t2, idx)
            self.add_dict_a_with_b(time_dict, t3, idx)

        for t in time_dict:
            tmp_intersect_list = time_dict[t]
            for i in range(len(tmp_intersect_list)):
                for j in range(i+1, len(tmp_intersect_list)):
                    c1 = candidate_list[tmp_intersect_list[i]]
                    c2 = candidate_list[tmp_intersect_list[j]]
                    if c1[0] == c2[0] or c1[1] == c2[1] or c1[2] == c2[2]:
                        self.add_dict_a_with_b(intersect_dict, tmp_intersect_list[i], tmp_intersect_list[j])
                        self.add_dict_a_with_b(intersect_dict, tmp_intersect_list[j], tmp_intersect_list[i])

        # greedy init
        chosen_list = []
        dislike_dict = {}
        for idx, c in enumerate(candidate_list):
            if idx not in dislike_dict:
                dislike_dict[idx] = []
                chosen_list.append(idx)
                if idx not in intersect_dict:
                    continue
                inter_points = intersect_dict[idx]
                for p in inter_points:
                    self.add_dict_a_with_b(dislike_dict, p, idx)
        # result search
        while True:
            stop = True
            idx = 0
            while idx < len(chosen_list):
                c = chosen_list[idx]
                if c not in intersect_dict:
                    idx += 1
                    continue

                inter_points = intersect_dict[c]   # find all points intersects with c
                possible_points = []
                for p in inter_points:
                    if len(dislike_dict[p]) == 1:    # if p only intersects with c, p is possible to be considered
                        possible_points.append(p)

                replace_flag = False
                for i in range(len(possible_points)):
                    p1 = possible_points[i]
                    if replace_flag:
                        break
                    for j in range(i+1, len(possible_points)):
                        p2 = possible_points[j]
                        if p2 not in intersect_dict[p1]:
                            replace_flag = True
                            stop = False
                            chosen_list.remove(c)
                            chosen_list.append(p1)
                            chosen_list.append(p2)
                            for tmp in intersect_dict[p1]:
                                self.add_dict_a_with_b(dislike_dict, tmp, p1)
                            for tmp in intersect_dict[p2]:
                                self.add_dict_a_with_b(dislike_dict, tmp, p2)
                            for tmp in intersect_dict[c]:
                                dislike_dict[tmp].remove(c)
                                if len(dislike_dict[tmp]) == 0 and tmp not in chosen_list:
                                    chosen_list.append(tmp)
                                    for tmp2 in intersect_dict[tmp]:
                                        self.add_dict_a_with_b(dislike_dict, tmp2, tmp)
                            break
                if not replace_flag:
                    idx += 1

            if stop:
                break
        return [candidate_list[idx] for idx in chosen_list]

    def add_dict_a_with_b(self, tar_dict, a, b):
        if a not in tar_dict:
            tar_dict[a] = [b]
        else:
            if b not in tar_dict[a]:
                tar_dict[a].append(b)


    def map_constraint_initialization(self, delta):
        'real_0-0.png'
        n = 128
        speedMax = 1800
        speedMin = 500
        torqueMax = 2600
        torqueMin = 0
        speedStep = int((speedMax - speedMin) / n) + 1
        torqueStep = int((torqueMax - torqueMin) / n) + 1

        filename = 'real_{}-0.png'.format(self.mapID)
        img = Image.open(os.path.join(MAP_PATH, filename)).convert('L')
        self.delta = delta
        self.map = list(np.array(img))

        points = []
        for i in range(n):
            for j in range(n):
                speed = speedMin + i * speedStep
                torque = torqueMin + i * torqueStep
                fuel = self.map[i][j]
                if fuel != 0:
                    points.append((speed, torque, fuel))
        self.kd = kdtree.create(points)



    def map_constraint(self, c):
        n = 128
        speedMax = 1800
        speedMin = 500
        torqueMax = 2600
        torqueMin = 0
        speedStep = int((speedMax - speedMin) / n) + 1
        torqueStep = int((torqueMax - torqueMin) / n) + 1

        speed = c[3]
        torque = c[4]
        fuel = c[5]

        if torque < torqueMin or torque > torqueMax:
            return False
        else:
            x = int((torque - torqueMin) / torqueStep)

        if speed < speedMin or speed > speedMax:
            return False
        else:
            y = int((speed - speedMin) / speedStep)

        fuel_ = float(self.map[x][y]) / 255 * 110

        if fuel_ == 0 or abs(fuel - fuel_) <= self.delta:
            return True
        return False

    def map_constraint_kd(self, c):
        speed = c[3]
        torque = c[4]
        # fuel was scaled into [0,255]
        fuel = float(c[5]) / 255 * 110
        point = (speed, torque, fuel)
        nn = self.kd.search_nn(point)[0].data
        dis = math.sqrt((point[0] - nn[0]) ** 2 + (point[1] - nn[1]) ** 2 + (point[2] - nn[2]) ** 2)
        if dis <= self.delta:
            return True
        return False
