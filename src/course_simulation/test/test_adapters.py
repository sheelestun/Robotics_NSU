import math

from nav_msgs.msg import Odometry
from course_simulation.drive_adapter import convert_drive
from course_simulation.odom_adapter import normalize_odometry


def test_drive_conversion_and_limits():
    straight, reason = convert_drive(0.7, 0.0, 0.05)
    assert reason == 'accepted'
    assert straight.linear.x == 0.7 and straight.angular.z == 0.0
    turn, reason = convert_drive(2.0, 0.8, 0.05)
    assert reason == 'accepted'
    assert turn.linear.x == 1.2
    assert math.isclose(turn.angular.z, 1.2 * math.tan(0.45) / 0.8)
    stopped, reason = convert_drive(0.0, 0.3, 0.05)
    assert reason == 'accepted'
    assert stopped.angular.z == 0.0


def test_rejects_stale_and_non_finite_drive():
    for args, expected in [((0.4, 0.1, 0.3), 'stale_or_future_stamp'),
                           ((float('nan'), 0.1, 0.0), 'non_finite'),
                           ((0.4, float('inf'), 0.0), 'non_finite')]:
        command, reason = convert_drive(*args)
        assert reason == expected
        assert command.linear.x == command.angular.z == 0.0


def test_odometry_frames_and_payload_preserved():
    incoming = Odometry()
    incoming.header.frame_id = 'course_ackermann/odom'
    incoming.header.stamp.sec = 42
    incoming.child_frame_id = 'course_ackermann/base_link'
    incoming.pose.pose.position.x = 1.25
    incoming.pose.pose.orientation.w = 1.0
    incoming.twist.twist.linear.x = 0.4
    incoming.pose.covariance[0] = 0.12
    incoming.twist.covariance[0] = 0.34
    outgoing = normalize_odometry(incoming)
    assert outgoing.header.frame_id == 'odom'
    assert outgoing.child_frame_id == 'base_link'
    assert outgoing.header.stamp.sec == 42
    assert outgoing.pose == incoming.pose
    assert outgoing.twist == incoming.twist
    assert incoming.header.frame_id == 'course_ackermann/odom'


def test_odometry_rejects_bad_frame_and_value():
    incoming = Odometry()
    incoming.header.frame_id = 'other/odom'
    incoming.child_frame_id = 'course_ackermann/base_link'
    assert normalize_odometry(incoming) is None
    incoming.header.frame_id = 'course_ackermann/odom'
    incoming.pose.pose.position.x = float('nan')
    assert normalize_odometry(incoming) is None
