#!/usr/bin/env bash
set -e
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y \
  ros-humble-moveit \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control \
  ros-humble-xacro ros-humble-joint-state-publisher-gui \
  python3-vcstool python3-rosdep
rosdep update || true
rosdep install --from-paths "$(dirname "$0")/../src" --ignore-src -r -y
