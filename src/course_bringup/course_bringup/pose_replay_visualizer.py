"""Visualize recorded sensor poses by moving a turtlesim turtle."""

from typing import List, Optional

import rclpy
from rclpy.node import Node
from turtlesim_msgs.msg import Pose
from turtlesim_msgs.srv import TeleportAbsolute

from course_bringup.pose_subscriber import subscriber_qos


def teleport_request_from_pose(pose: Pose) -> TeleportAbsolute.Request:
    """Convert a recorded pose into a turtlesim teleport request."""
    request = TeleportAbsolute.Request()
    request.x = pose.x
    request.y = pose.y
    request.theta = pose.theta
    return request


class PoseReplayVisualizer(Node):
    """Move turtle1 through poses received from an MCAP replay."""

    def __init__(self) -> None:
        super().__init__('pose_replay_visualizer')
        self._latest_pose: Optional[Pose] = None
        self._pending_request = None
        self._first_pose_logged = False
        self._service_warning_logged = False

        self._teleport_client = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute',
        )
        self._subscription = self.create_subscription(
            Pose,
            'sensor_pose',
            self._store_pose,
            subscriber_qos('best_effort'),
        )
        self._timer = self.create_timer(1.0 / 60.0, self._move_turtle)
        self.get_logger().info(
            'waiting for best_effort sensor_pose replay',
        )

    def _store_pose(self, pose: Pose) -> None:
        self._latest_pose = pose

    def _move_turtle(self) -> None:
        if self._latest_pose is None:
            return
        if not self._teleport_client.service_is_ready():
            if not self._service_warning_logged:
                self.get_logger().warning(
                    'waiting for /turtle1/teleport_absolute',
                )
                self._service_warning_logged = True
            return
        if self._pending_request is not None and not self._pending_request.done():
            return

        pose = self._latest_pose
        self._latest_pose = None
        self._pending_request = self._teleport_client.call_async(
            teleport_request_from_pose(pose),
        )
        if not self._first_pose_logged:
            self.get_logger().info(
                f'visualizing replay from x={pose.x:.3f}, y={pose.y:.3f}',
            )
            self._first_pose_logged = True


def main(args: Optional[List[str]] = None) -> None:
    """Run the replay visualizer until ROS 2 requests shutdown."""
    rclpy.init(args=args)
    node = PoseReplayVisualizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
