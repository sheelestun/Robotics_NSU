"""Subscribe to relayed poses with a configurable reliability policy."""

from typing import List, Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim_msgs.msg import Pose


def subscriber_qos(reliability: str) -> QoSProfile:
    """Build the requested reliable or best-effort subscriber profile."""
    policies = {
        'reliable': ReliabilityPolicy.RELIABLE,
        'best_effort': ReliabilityPolicy.BEST_EFFORT,
    }
    try:
        policy = policies[reliability]
    except KeyError as error:
        raise ValueError(
            'subscriber reliability must be reliable or best_effort',
        ) from error

    return QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
        reliability=policy,
    )


class PoseSubscriber(Node):
    """Log receipt of sensor poses using the launch-selected QoS."""

    def __init__(self) -> None:
        super().__init__('pose_subscriber')
        reliability = str(
            self.declare_parameter('reliability', 'reliable').value,
        )
        self._message_count = 0
        self._subscription = self.create_subscription(
            Pose,
            'sensor_pose',
            self._receive_pose,
            subscriber_qos(reliability),
        )
        self.get_logger().info(
            f'waiting for sensor_pose with {reliability} QoS',
        )

    def _receive_pose(self, pose: Pose) -> None:
        self._message_count += 1
        if self._message_count == 1:
            self.get_logger().info(
                f'first sensor_pose received: x={pose.x:.3f}, y={pose.y:.3f}',
            )


def main(args: Optional[List[str]] = None) -> None:
    """Run the diagnostic subscriber until ROS 2 requests shutdown."""
    rclpy.init(args=args)
    node = PoseSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
