"""ROS 2 node that publishes configurable commands from a turtlesim pose."""

from math import isfinite
from typing import List, Optional, Sequence

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from turtlesim_msgs.msg import Pose


def parameter_validation_error(
    linear_speed: float,
    turn_rate: float,
    publish_hz: float,
) -> Optional[str]:
    """Return an error for invalid motion parameters, otherwise ``None``."""
    if not isfinite(linear_speed) or not 0.0 <= linear_speed <= 1.0:
        return 'linear_speed must be finite and between 0.0 and 1.0 m/s'
    if not isfinite(turn_rate) or not -1.0 <= turn_rate <= 1.0:
        return 'turn_rate must be finite and between -1.0 and 1.0 rad/s'
    if not isfinite(publish_hz) or not 1.0 <= publish_hz <= 30.0:
        return 'publish_hz must be finite and between 1.0 and 30.0 Hz'
    return None


def command_from_pose(
    pose: Optional[Pose],
    linear_speed: float = 0.5,
    turn_rate: float = 0.3,
) -> Twist:
    """Return a stopped command without a pose and a patrol command otherwise."""
    command = Twist()

    if pose is not None:
        command.linear.x = linear_speed
        command.angular.z = turn_rate

    return command


class Patrol(Node):
    """Store the latest turtle pose and publish velocity commands periodically."""

    def __init__(self) -> None:
        super().__init__('patrol')

        self._last_pose: Optional[Pose] = None
        self._linear_speed = float(self.declare_parameter('linear_speed', 0.5).value)
        self._turn_rate = float(self.declare_parameter('turn_rate', 0.3).value)
        self._publish_hz = float(self.declare_parameter('publish_hz', 10.0).value)

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
        self._timer = self.create_timer(
            1.0 / self._publish_hz,
            self._timer_callback,
        )
        self.add_on_set_parameters_callback(self._validate_parameters)
        self.add_post_set_parameters_callback(self._apply_parameters)

    def _pose_callback(self, pose: Pose) -> None:
        self._last_pose = pose

    def _timer_callback(self) -> None:
        command = command_from_pose(
            self._last_pose,
            self._linear_speed,
            self._turn_rate,
        )
        self._publisher.publish(command)

    def _parameter_values(
        self,
        parameters: Sequence[Parameter],
    ) -> tuple[float, float, float]:
        values = {
            'linear_speed': self._linear_speed,
            'turn_rate': self._turn_rate,
            'publish_hz': self._publish_hz,
        }
        for parameter in parameters:
            if parameter.name in values:
                values[parameter.name] = float(parameter.value)
        return (
            values['linear_speed'],
            values['turn_rate'],
            values['publish_hz'],
        )

    def _validate_parameters(
        self,
        parameters: List[Parameter],
    ) -> SetParametersResult:
        try:
            values = self._parameter_values(parameters)
        except (TypeError, ValueError):
            return SetParametersResult(
                successful=False,
                reason='motion parameters must be floating-point numbers',
            )

        error = parameter_validation_error(*values)
        return SetParametersResult(
            successful=error is None,
            reason=error or '',
        )

    def _apply_parameters(self, parameters: List[Parameter]) -> None:
        linear_speed, turn_rate, publish_hz = self._parameter_values(parameters)
        frequency_changed = publish_hz != self._publish_hz

        self._linear_speed = linear_speed
        self._turn_rate = turn_rate

        if frequency_changed:
            self._timer.cancel()
            self.destroy_timer(self._timer)
            self._publish_hz = publish_hz
            self._timer = self.create_timer(
                1.0 / self._publish_hz,
                self._timer_callback,
            )


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
