#!/usr/bin/env bash
set -e
source /opt/ros/humble/setup.bash
for p in moveit_core moveit_ros_move_group controller_manager joint_trajectory_controller joint_state_broadcaster gazebo_ros2_control; do
  if ros2 pkg prefix "$p" >/dev/null 2>&1; then echo "[OK] $p"; else echo "[MISSING] $p"; fi
done
