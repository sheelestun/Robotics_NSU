import math

from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.time import Time


def convert_drive(speed, steering_angle, age_seconds):
    command = Twist()
    if not all(math.isfinite(value) for value in
               (speed, steering_angle, age_seconds)):
        return command, 'non_finite'
    if age_seconds > 0.25 or age_seconds < -0.05:
        return command, 'stale_or_future_stamp'
    velocity = min(max(speed, 0.0), 1.2)
    steering = min(max(steering_angle, -0.45), 0.45)
    command.linear.x = velocity
    command.angular.z = velocity * math.tan(steering) / 0.8
    return command, 'accepted'


class DriveAdapter(Node):
    def __init__(self):
        super().__init__('drive_adapter')
        self.declare_parameter('safe_topic', '/drive/safe')
        self.declare_parameter('gz_command_topic', '/vehicle/gz_cmd_vel')
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.publisher = self.create_publisher(
            Twist, self.get_parameter('gz_command_topic').value, qos)
        self.subscription = self.create_subscription(
            AckermannDriveStamped, self.get_parameter('safe_topic').value,
            self.on_drive, qos)

    def on_drive(self, message):
        age = (self.get_clock().now() - Time.from_msg(message.header.stamp))
        command, reason = convert_drive(
            message.drive.speed, message.drive.steering_angle,
            age.nanoseconds / 1e9)
        self.publisher.publish(command)
        if reason != 'accepted':
            self.get_logger().warning('Rejected drive command: ' + reason)


def main():
    rclpy.init()
    node = DriveAdapter()
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
