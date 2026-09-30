"""Tests for patrol velocity command selection."""

from patrol.patrol import command_from_pose
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
