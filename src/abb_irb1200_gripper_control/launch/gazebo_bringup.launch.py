from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    desc_pkg='abb_irb1200_gripper_description'
    xacro=os.path.join(get_package_share_directory(desc_pkg),'urdf','abb_irb1200_gripper.urdf.xacro')
    robot_description={'robot_description': Command(['xacro ',xacro,' use_fake_hardware:=true use_gazebo:=true'])}
    gazebo=IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('gazebo_ros'),'launch','gazebo.launch.py')))
    return LaunchDescription([
      gazebo,
      Node(package='robot_state_publisher', executable='robot_state_publisher', parameters=[robot_description]),
      Node(package='gazebo_ros', executable='spawn_entity.py', arguments=['-topic','robot_description','-entity','abb_irb1200_gripper'], output='screen'),
      Node(package='controller_manager', executable='spawner', arguments=['joint_state_broadcaster','--controller-manager','/controller_manager']),
      Node(package='controller_manager', executable='spawner', arguments=['arm_controller','--controller-manager','/controller_manager']),
      Node(package='controller_manager', executable='spawner', arguments=['gripper_controller','--controller-manager','/controller_manager'])])
