"""Launch turtlesim, patrol, pose relay, QoS subscriber, and optional bag."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Create the configurable PR05 launch description."""
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')
    sensor_topic = PythonExpression([
        "'/' + '",
        namespace,
        "'.strip('/') + '/sensor_pose'",
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='robot_a',
            description='Namespace for patrol and sensor nodes.',
        ),
        DeclareLaunchArgument(
            'record',
            default_value='false',
            description='Record the sensor stream to an MCAP bag.',
        ),
        DeclareLaunchArgument(
            'bag_dir',
            default_value='evidence/pr05/bag',
            description='Output directory passed to ros2 bag record.',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability',
            default_value='reliable',
            choices=['reliable', 'best_effort'],
            description='Reliability requested by the diagnostic subscriber.',
        ),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        Node(
            package='patrol',
            executable='patrol',
            namespace=namespace,
            output='screen',
            remappings=[
                ('cmd_vel', '/turtle1/cmd_vel'),
            ],
        ),
        Node(
            package='course_bringup',
            executable='pose_relay',
            namespace=namespace,
            output='screen',
            remappings=[
                ('pose', '/turtle1/pose'),
            ],
        ),
        Node(
            package='course_bringup',
            executable='pose_subscriber',
            namespace=namespace,
            output='screen',
            parameters=[{
                'reliability': subscriber_reliability,
            }],
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-s', 'mcap',
                '-o', bag_dir,
                '--topics', sensor_topic,
            ],
            output='screen',
            condition=IfCondition(record),
        ),
    ])
