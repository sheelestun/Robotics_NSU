"""Relay turtlesim poses through a best-effort sensor topic."""

from typing import List, Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim_msgs.msg import Pose


def sensor_qos() -> QoSProfile:
    """Return the sensor publisher QoS required by PR05."""
    return QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
        reliability=ReliabilityPolicy.BEST_EFFORT,
    )


class PoseRelay(Node):
    """Republish poses using a relative best-effort sensor topic."""

    def __init__(self) -> None:
        super().__init__('pose_relay')
        self._publisher = self.create_publisher(
            Pose,
            'sensor_pose',
            sensor_qos(),
        )
        self._subscription = self.create_subscription(
            Pose,
            'pose',
            self._relay_pose,
            10,
        )
        self.get_logger().info('relaying pose to sensor_pose with best_effort QoS')

    def _relay_pose(self, pose: Pose) -> None:
        self._publisher.publish(pose)


def main(args: Optional[List[str]] = None) -> None:
    """Run the pose relay until ROS 2 requests shutdown."""
    rclpy.init(args=args)
    node = PoseRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
