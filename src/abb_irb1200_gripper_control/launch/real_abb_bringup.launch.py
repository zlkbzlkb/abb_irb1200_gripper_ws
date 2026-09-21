"""Real ABB bringup wrapper.
Requires PickNikRobotics/abb_ros2 (humble branch) and a correctly configured ABB controller.
The base arm is launched through abb_bringup; the gripper remains a separate device/controller.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    abb_bringup = get_package_share_directory('abb_bringup')
    return LaunchDescription([
      DeclareLaunchArgument('rws_ip', default_value='192.168.125.1'),
      DeclareLaunchArgument('rws_port', default_value='80'),
      IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(abb_bringup,'launch','abb_control.launch.py')),
        launch_arguments={
          'description_package':'abb_irb1200_support',
          'description_file':'irb1200_5_90.xacro',
          'moveit_config_package':'abb_irb1200_5_90_moveit_config',
          'use_fake_hardware':'false',
          'rws_ip':LaunchConfiguration('rws_ip'),
          'rws_port':LaunchConfiguration('rws_port'),
          'launch_rviz':'false'}.items())])
