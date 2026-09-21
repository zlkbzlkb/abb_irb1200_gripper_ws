from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os, yaml

def load_yaml(pkg, rel):
    with open(os.path.join(get_package_share_directory(pkg), rel), 'r') as f:
        return yaml.safe_load(f)

def generate_launch_description():
    desc_pkg='abb_irb1200_gripper_description'; cfg_pkg='abb_irb1200_gripper_moveit_config'
    xacro=os.path.join(get_package_share_directory(desc_pkg),'urdf','abb_irb1200_gripper.urdf.xacro')
    urdf={'robot_description': Command(['xacro ', xacro, ' use_fake_hardware:=true'])}
    srdf_path=os.path.join(get_package_share_directory(cfg_pkg),'config','abb_irb1200_gripper.srdf')
    srdf={'robot_description_semantic': open(srdf_path).read()}
    kin={'robot_description_kinematics': load_yaml(cfg_pkg,'config/kinematics.yaml')}
    limits={'robot_description_planning': load_yaml(cfg_pkg,'config/joint_limits.yaml')}
    ompl=load_yaml(cfg_pkg,'config/ompl_planning.yaml')
    ctrls=load_yaml(cfg_pkg,'config/moveit_controllers.yaml')
    return LaunchDescription([
      Node(package='moveit_ros_move_group', executable='move_group', output='screen', parameters=[urdf,srdf,kin,limits,ompl,ctrls,{'planning_scene_monitor_options': {'publish_planning_scene': True,'publish_geometry_updates': True,'publish_state_updates': True,'publish_transforms_updates': True}}]),
      Node(package='rviz2', executable='rviz2', output='screen', parameters=[urdf,srdf,kin])])
