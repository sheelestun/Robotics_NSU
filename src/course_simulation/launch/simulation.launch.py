from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (Command, EnvironmentVariable, LaunchConfiguration,
                                  PathJoinSubstitution)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    simulation = FindPackageShare('course_simulation')
    description = FindPackageShare('course_description')
    model = PathJoinSubstitution([description, 'urdf', 'vehicle.urdf.xacro'])
    world = LaunchConfiguration('world')
    bridge_config = LaunchConfiguration('bridge_config')
    headless = LaunchConfiguration('headless')
    namespace = LaunchConfiguration('namespace')
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=PathJoinSubstitution(
            [simulation, 'worlds', 'mcity-minimal.sdf'])),
        DeclareLaunchArgument('bridge_config', default_value=PathJoinSubstitution(
            [simulation, 'config', 'bridge.yaml'])),
        DeclareLaunchArgument('headless', default_value='true'),
        DeclareLaunchArgument('namespace', default_value=''),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', [
            PathJoinSubstitution([simulation, 'models']), ':',
            EnvironmentVariable('GZ_SIM_RESOURCE_PATH', default_value='')]),
        ExecuteProcess(cmd=['gz', 'sim', '-s', '-r', '--headless-rendering', world],
                       output='screen', condition=IfCondition(headless)),
        ExecuteProcess(cmd=['gz', 'sim', '-r', world], output='screen',
                       condition=UnlessCondition(headless)),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             namespace=namespace, output='screen',
             parameters=[{'robot_description': Command(['xacro ', model]),
                          'use_sim_time': True}]),
        Node(package='ros_gz_bridge', executable='parameter_bridge',
             namespace=namespace, output='screen',
             parameters=[{'config_file': bridge_config}]),
        Node(package='course_simulation', executable='drive_adapter',
             namespace=namespace, output='screen',
             parameters=[{'use_sim_time': True}]),
        Node(package='course_simulation', executable='odom_adapter',
             namespace=namespace, output='screen',
             parameters=[{'use_sim_time': True}]),
    ])
