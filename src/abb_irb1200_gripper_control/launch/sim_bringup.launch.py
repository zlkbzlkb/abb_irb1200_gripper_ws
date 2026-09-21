from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    desc_pkg='abb_irb1200_gripper_description'
    xacro=os.path.join(get_package_share_directory(desc_pkg),'urdf','abb_irb1200_gripper.urdf.xacro')
    controllers=os.path.join(get_package_share_directory(desc_pkg),'config','controllers.yaml')
    robot_description={'robot_description': Command(['xacro ',xacro,' use_fake_hardware:=true use_gazebo:=false'])}
    return LaunchDescription([
      Node(package='robot_state_publisher', executable='robot_state_publisher', parameters=[robot_description], output='screen'),
      Node(package='controller_manager', executable='ros2_control_node', parameters=[robot_description,controllers], output='screen'),
      Node(package='controller_manager', executable='spawner', arguments=['joint_state_broadcaster','--controller-manager','/controller_manager']),
      Node(package='controller_manager', executable='spawner', arguments=['arm_controller','--controller-manager','/controller_manager']),
      Node(package='controller_manager', executable='spawner', arguments=['gripper_controller','--controller-manager','/controller_manager'])])
