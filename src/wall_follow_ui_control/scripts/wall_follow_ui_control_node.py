#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

from roboracer_interfaces.msg import CarControlWallFollow
from std_msgs.msg import Float32
from sensor_msgs.msg import LaserScan

import numpy as np

class WallFollowUiControlNode(Node):
    def __init__(self):
        super().__init__("wall_follow_ui_control_node")
        self.get_logger().info("wall follow ui control node")

        self.desired_dist_from_wall = 0.5

        self.theta1 = np.deg2rad(20)
        self.theta2 = np.deg2rad(90)

        self.kp = 2.4
        self.kd = 0.8
        self.ki = 0.0

        self.throttle = 0.2
        self.lookahead_dist = 0.8

        self.prev_error = 0.0
        self.error = 0.0

        qos_profile = QoSProfile(depth=10)

        # Subscriber Topics
        wall_follow_params_sub_topic = "wall_follow_params"
        lidar_sub_topic = '/autodrive/f1tenth_1/lidar'
        # throttle_sub_topic = '/autodrive/f1tenth_1/throttle'

        self.wall_follow_params_sub_ = self.create_subscription(CarControlWallFollow, wall_follow_params_sub_topic, self.wall_follow_params_callback, qos_profile)
        self.lidar_sub_ = self.create_subscription(LaserScan, lidar_sub_topic, self.scan_callback, qos_profile)

        # Publisher topics
        steering_pub_topic = '/autodrive/f1tenth_1/steering_command'
        throttle_pub_topic = '/autodrive/f1tenth_1/throttle_command'

        self.throttle_pub = self.create_publisher(Float32, throttle_pub_topic, qos_profile)
        self.steering_pub = self.create_publisher(Float32, steering_pub_topic, qos_profile)



    def wall_follow_params_callback(self, msg):

        if self.kp != msg.kp:
            self.kp = msg.kp 

        if self.kd != msg.kd:
            self.kd = msg.kd

        if self.ki != msg.ki:
            self.ki = msg.ki 

        if self.throttle != msg.throttle:
            self.throttle = msg.throttle
        
        if self.lookahead_dist != msg.lookahead_dist:
            self.lookahead_dist = msg.lookahead_dist

        


    def get_range(self, range_data, angle):
        """
        Simple helper to return the corresponding range measurement at a given angle. Make sure you take care of NaNs and infs.

        Args:
            range_data: single range array from the LiDAR
            angle: between angle_min and angle_max of the LiDAR

        Returns:
            range: range measurement in meters at the given angle

        """

        index = int((angle - range_data['angles'][0]) / range_data['angle_increment'])

        return_range = range_data['ranges'][index]

        if np.isnan(return_range) or np.isinf(return_range):
            return 0.0
        
        return return_range

    def get_error(self, range_data, dist):
        """
        Calculates the error to the wall. Follow the wall to the left (going counter clockwise in the Levine loop). You potentially will need to use get_range()

        Args:
            range_data: single range array from the LiDAR
            dist: desired distance to the wall

        Returns:
            error: calculated error
        """

        #TODO:implement

        # self.lookahead_dist = self.speed * 0.8

        a = self.get_range(range_data, self.theta1)
        b = self.get_range(range_data, self.theta2)


        # self.get_logger().info(f"a: {a}, b: {b}", throttle_duration_sec=1)

        theta = self.theta2 - self.theta1

        # self.get_logger().info(f"theta: {theta}", throttle_duration_sec=1)

        alpha = np.arctan2((a*np.cos(theta) - b), (a*np.sin(theta)))

        # self.get_logger().info(f"alpha: {alpha}", throttle_duration_sec=1)

        dt = b * np.cos(alpha)

        dt1 = dt + self.lookahead_dist*np.sin(alpha)

        # self.get_logger().info(f"dt: {dt}, dt1: {dt1}", throttle_duration_sec=1)

        error = dist - dt1

        # self.get_logger().info(f"Error: {error}", throttle_duration_sec=1)

        return error
    
    def publish_to_car(self, steering_angle, throttle):
        """
        Publish the steering angle and throttle to the car.

        Args:
            steering_angle: Steering angle in radians
            throttle: Throttle value
        Returns:
            None
        """

        self.get_logger().info(f"Steering angle: {steering_angle}, Throttle: {throttle}", throttle_duration_sec=1.0)

        steering_angle = np.clip(steering_angle, -1, 1) # Limit steering angle to [-30, 30] degrees

        steering_msg = Float32()
        steering_msg.data = steering_angle 

        throttle_msg = Float32()
        throttle_msg.data = throttle 

        self.steering_pub.publish(steering_msg)
        self.throttle_pub.publish(throttle_msg)

    def pid_control(self, error, throttle):
        """
        Based on the calculated error, publish vehicle control

        Args:
            error: calculated error
            throttle: desired throttle

        Returns:
            None
        """
        angle = 0.0
        # TODO: Use kp, ki & kd to implement a PID controller

        proportional = self.kp * error

        derivative = self.kd * (error - self.prev_error)

        integral = self.ki * (error + self.prev_error)

        if np.abs(integral) > 1.0:
            integral = 0.0

        angle = proportional + derivative + integral
        angle *= -1
        # angle = np.clip(angle, -0.8, 0.8)

        # If throttle is 404, then set throttle based on angle
        if throttle == 404:
            if np.abs(angle) <= np.deg2rad(10):
                throttle = 1.0
            elif np.abs(angle) <= np.deg2rad(20):
                throttle = 0.75
            else:
                throttle = 0.5

        # self.get_logger().info(f"Angle: {angle}", skip_first=True, throttle_duration_sec=1.0)
        # self.get_logger().info(f"error: {error}", skip_first=True, throttle_duration_sec=1.0)
        
        # TODO: fill in drive message and publish
        self.publish_to_car(angle, throttle)

    def scan_callback(self, msg):
        """
        Callback function for LaserScan messages. Calculate the error and publish the drive message in this function.

        Args:
            msg: Incoming LaserScan message

        Returns:
            None
        """

        range_data = {
            'ranges': msg.ranges,
            'angles': np.linspace(msg.angle_min, msg.angle_max, len(msg.ranges)),
            'angle_increment': msg.angle_increment
        }

        # TODO: replace with error calculated by get_error()
        self.prev_error = self.error

        # TODO: calculate desired car velocity based on error
        self.error = self.get_error(range_data, self.desired_dist_from_wall)

        # TODO: calculate desired car velocity based on error
        # self.pid_control(self.error, self.speed)

        # TODO: calculate desired car velocity based on error
        self.pid_control(self.error, self.throttle)
    
def main(args=None):
    rclpy.init(args=args)
    wall_follow_ui_control_node =  WallFollowUiControlNode()
    rclpy.spin(wall_follow_ui_control_node)
    wall_follow_ui_control_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()