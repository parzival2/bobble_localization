from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory('bobble_localization')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    namespace = LaunchConfiguration('namespace')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('namespace', default_value='bobble'),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            namespace=namespace,
            output='screen',
            parameters=[ekf_config, {'use_sim_time': use_sim_time}],
            remappings=[('odometry/filtered', 'odom/filtered')],
        ),
    ])
