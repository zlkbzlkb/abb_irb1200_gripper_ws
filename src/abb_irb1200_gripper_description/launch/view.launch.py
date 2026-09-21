from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    xacro = os.path.join(get_package_share_directory('abb_irb1200_gripper_description'),'urdf','abb_irb1200_gripper.urdf.xacro')
    desc = {'robot_description': Command(['xacro ', xacro])}
    return LaunchDescription([
        Node(package='robot_state_publisher', executable='robot_state_publisher', parameters=[desc]),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui'),
        Node(package='rviz2', executable='rviz2')])
