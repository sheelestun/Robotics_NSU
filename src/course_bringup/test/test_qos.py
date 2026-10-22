"""Tests for the PR05 publisher and subscriber QoS profiles."""

from course_bringup.pose_relay import sensor_qos
from course_bringup.pose_replay_visualizer import teleport_request_from_pose
from course_bringup.pose_subscriber import subscriber_qos
import pytest
from rclpy.qos import ReliabilityPolicy
from turtlesim_msgs.msg import Pose


def test_sensor_publisher_is_best_effort() -> None:
    """Publish the relayed sensor stream with best-effort reliability."""
    assert sensor_qos().reliability == ReliabilityPolicy.BEST_EFFORT


@pytest.mark.parametrize(
    ('name', 'expected'),
    [
        ('reliable', ReliabilityPolicy.RELIABLE),
        ('best_effort', ReliabilityPolicy.BEST_EFFORT),
    ],
)
def test_subscriber_reliability_is_configurable(
    name: str,
    expected: ReliabilityPolicy,
) -> None:
    """Map both supported launch values to their ROS policies."""
    assert subscriber_qos(name).reliability == expected


def test_unknown_subscriber_reliability_is_rejected() -> None:
    """Reject values outside the two launch-supported policies."""
    with pytest.raises(ValueError):
        subscriber_qos('unknown')


def test_recorded_pose_is_converted_to_teleport_request() -> None:
    """Copy the recorded position and heading into a teleport request."""
    pose = Pose(x=1.5, y=2.5, theta=0.75)

    request = teleport_request_from_pose(pose)

    assert request.x == pytest.approx(1.5)
    assert request.y == pytest.approx(2.5)
    assert request.theta == pytest.approx(0.75)
