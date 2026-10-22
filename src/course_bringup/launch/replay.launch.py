"""Launch turtlesim and visualize poses replayed from an MCAP bag."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Create the PR05 graphical replay launch description."""
    namespace = LaunchConfiguration('namespace')

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='robot_a',
            description='Namespace used by the recorded sensor topic.',
        ),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        Node(
            package='course_bringup',
            executable='pose_replay_visualizer',
            namespace=namespace,
            output='screen',
            parameters=[{
                'use_sim_time': True,
            }],
        ),
    ])
