from copy import deepcopy
import math

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from tf2_ros import TransformBroadcaster


def normalize_odometry(message):
    if (message.header.frame_id != 'course_ackermann/odom' or
            message.child_frame_id != 'course_ackermann/base_link'):
        return None
    pose = message.pose.pose
    twist = message.twist.twist
    numbers = [pose.position.x, pose.position.y, pose.position.z,
               pose.orientation.x, pose.orientation.y,
               pose.orientation.z, pose.orientation.w,
               twist.linear.x, twist.linear.y, twist.linear.z,
               twist.angular.x, twist.angular.y, twist.angular.z,
               *message.pose.covariance, *message.twist.covariance]
    if not all(math.isfinite(value) for value in numbers):
        return None
    result = deepcopy(message)
    result.header.frame_id = 'odom'
    result.child_frame_id = 'base_link'
    return result


class OdomAdapter(Node):
    def __init__(self):
        super().__init__('odom_adapter')
        self.declare_parameter('input_topic', '/vehicle/odom_gz')
        self.declare_parameter('output_topic', '/vehicle/odom')
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.publisher = self.create_publisher(
            Odometry, self.get_parameter('output_topic').value, qos)
        self.subscription = self.create_subscription(
            Odometry, self.get_parameter('input_topic').value,
            self.on_odometry, qos)
        self.broadcaster = TransformBroadcaster(self)

    def on_odometry(self, message):
        odom = normalize_odometry(message)
        if odom is None:
            self.get_logger().warning('Rejected odometry: frame or value')
            return
        self.publisher.publish(odom)
        transform = TransformStamped()
        transform.header = deepcopy(odom.header)
        transform.child_frame_id = odom.child_frame_id
        transform.transform.translation.x = odom.pose.pose.position.x
        transform.transform.translation.y = odom.pose.pose.position.y
        transform.transform.translation.z = odom.pose.pose.position.z
        transform.transform.rotation = deepcopy(odom.pose.pose.orientation)
        self.broadcaster.sendTransform(transform)


def main():
    rclpy.init()
    node = OdomAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception:
        if rclpy.ok():
            raise
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
