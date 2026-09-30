"""ROS 2 node that publishes commands from the latest turtlesim pose."""

from typing import List, Optional

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim_msgs.msg import Pose


def command_from_pose(pose: Optional[Pose]) -> Twist:
    """Return a stopped command without a pose and a patrol command otherwise."""
    command = Twist()

    if pose is not None:
        command.linear.x = 0.5
        command.angular.z = 0.3

    return command


class Patrol(Node):
    """Store the latest turtle pose and publish velocity commands periodically."""

    def __init__(self) -> None:
        super().__init__('patrol')

        self._last_pose: Optional[Pose] = None

        self._publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10,
        )
        self._subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._pose_callback,
            10,
        )
        self._timer = self.create_timer(0.1, self._timer_callback)

    def _pose_callback(self, pose: Pose) -> None:
        self._last_pose = pose

    def _timer_callback(self) -> None:
        command = command_from_pose(self._last_pose)
        self._publisher.publish(command)


def main(args: Optional[List[str]] = None) -> None:
    """Run the patrol node until ROS 2 requests shutdown."""
    rclpy.init(args=args)
    node = Patrol()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
