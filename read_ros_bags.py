import os
import math
import dvrk
import rospy
import rosbag
import numpy as np 
import csv
import time
import argparse

class RosbagParser():

    def __init__(self, args):
        
        self.args = args
        for k, v in args.__dict__.items():
            setattr(self, k, v)

    def single_datapoint_processing(self, file_name): # parses data into the global dictionaries
   
        bag = rosbag.Bag(self.folder+file_name, 'r')

        force_sensor = []
        force_sensor_timestamps = []
        joint_position = []
        joint_velocity = []
        joint_effort = []
        joint_timestamps = []

        length_force_sensor = 0
        length_state_joint_current = 0

        print("Processing " + file_name)
        state_joint_current = bag.read_messages(topics=['/dvrk/PSM1/state_joint_current'])
        for topic, msg, t in state_joint_current:
            joint_timestamps.append(t.secs+t.nsecs*10**-9)

            # handles velocity for six joints
            joint_velocity.append(list(msg.velocity))

            # handles position for six joints
            joint_position.append(list(msg.position))

            # handles effort for six joints
            joint_effort.append(list(msg.effort))

            length_state_joint_current+=1

        wrench = bag.read_messages(topics=['/atinetft/wrench'])
        for topic, msg, t in wrench:
            timestamps = t.secs+t.nsecs*10**-9
            force_sensor_timestamps.append(timestamps)
            x = msg.wrench.force.x
            y = msg.wrench.force.y
            z = msg.wrench.force.z # the sensor is probably most accurate in the z direction
            force_sensor.append(list((x,y,z)))
            length_force_sensor+=1

        bag.close()
                                      
        print("Processed wrench: counts: {}".format(length_force_sensor))
        print("Processed state joint current: count: {}".format(length_state_joint_current))
        print("")

        joints = np.column_stack((joint_timestamps, joint_position, joint_velocity, joint_effort))
        force_sensor = np.column_stack((force_sensor_timestamps,force_sensor))

        return joints, force_sensor

    def write(self, joints, force_sensor):
        file_name = self.output + self.prefix + str(self.index)
        np.savetxt(file_name + "_joint_values.csv", joints, delimiter=',')
        np.savetxt(file_name + "_force_sensor.csv", force_sensor, delimiter=',')
        
    def parse_bags(self):

        print("\nParsing\n")
        files = os.listdir(self.folder)
        files.sort()
        for file_name in files:
            if file_name.endswith('.bag'):
                joints, force_sensor = self.single_datapoint_processing(file_name)
                self.write(joints, force_sensor)
                self.index += 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', default='../data/', type=str, help='Path to Rosbag folder')
    parser.add_argument('-o', '--output', default='./parsed_data/', type=str, help='Path to write out parsed csv')
    parser.add_argument('--prefix', default='bag_', type=str, help='Prefix for the output csv names')
    parser.add_argument('--index', default=0, type=int, help='Prefix for the output csv names')
    args = parser.parse_args()
    start = time.time()
    rosbag_parser = RosbagParser(args)
    rosbag_parser.parse_bags()
    print("Parsing complete") 
    end = time.time()
    print("The entire process takes {} seconds".format(end - start))

if __name__ == "__main__":
    main()
