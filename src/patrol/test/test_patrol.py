"""Tests for patrol commands and parameter validation."""

from math import nan

from patrol.patrol import command_from_pose, parameter_validation_error
import pytest
from turtlesim_msgs.msg import Pose


def test_command_without_pose_is_zero() -> None:
    """Return a stopped command before the first pose is received."""
    command = command_from_pose(None)

    assert command.linear.x == 0.0
    assert command.linear.y == 0.0
    assert command.linear.z == 0.0
    assert command.angular.x == 0.0
    assert command.angular.y == 0.0
    assert command.angular.z == 0.0


def test_command_with_pose_moves_and_turns() -> None:
    """Return the required patrol command after receiving a pose."""
    pose = Pose()
    pose.x = 5.5
    pose.y = 5.5
    pose.theta = 0.0

    command = command_from_pose(pose)

    assert command.linear.x == 0.5
    assert command.angular.z == 0.3


def test_command_uses_configured_speeds() -> None:
    """Use the current parameter values in the published command."""
    command = command_from_pose(Pose(), linear_speed=0.8, turn_rate=-0.4)

    assert command.linear.x == 0.8
    assert command.angular.z == -0.4


@pytest.mark.parametrize('publish_hz', [10.0, 5.0])
def test_valid_frequency_is_accepted(publish_hz: float) -> None:
    """Accept both the initial and an ordinary updated frequency."""
    assert parameter_validation_error(0.5, 0.3, publish_hz) is None


@pytest.mark.parametrize('publish_hz', [0.0, -1.0, nan])
def test_invalid_frequency_is_rejected(publish_hz: float) -> None:
    """Reject zero, negative and non-finite publish frequencies."""
    error = parameter_validation_error(0.5, 0.3, publish_hz)

    assert error is not None
    assert 'publish_hz' in error


@pytest.mark.parametrize(
    ('linear_speed', 'turn_rate'),
    [(-0.1, 0.3), (1.1, 0.3), (nan, 0.3), (0.5, -1.1), (0.5, 1.1), (0.5, nan)],
)
def test_invalid_motion_values_are_rejected(
    linear_speed: float,
    turn_rate: float,
) -> None:
    """Reject speeds outside their finite documented ranges."""
    assert parameter_validation_error(linear_speed, turn_rate, 10.0) is not None
