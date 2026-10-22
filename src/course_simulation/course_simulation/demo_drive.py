from time import sleep

from ackermann_msgs.msg import AckermannDriveStamped
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy


def main():
    rclpy.init()
    node = Node('demo_drive')
    node.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])
    qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
    publisher = node.create_publisher(AckermannDriveStamped, '/drive/safe', qos)
    start = None
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            now = node.get_clock().now()
            if now.nanoseconds == 0:
                continue
            if start is None:
                start = now
            elapsed = (now - start).nanoseconds / 1e9
            message = AckermannDriveStamped()
            message.header.stamp = now.to_msg()
            message.drive.speed = 0.5 if elapsed < 6.0 else 0.0
            message.drive.steering_angle = 0.1 if elapsed < 6.0 else 0.0
            publisher.publish(message)
            if elapsed >= 7.0:
                break
            sleep(0.2)
    finally:
        node.destroy_node()
        rclpy.shutdown()
