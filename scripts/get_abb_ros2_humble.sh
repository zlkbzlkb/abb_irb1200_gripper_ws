#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/src"
if [ ! -d abb_ros2 ]; then
  git clone -b humble https://github.com/PickNikRobotics/abb_ros2.git
fi
cd abb_ros2
vcs import < abb.repos
cd "$ROOT"
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
printf 'ABB ROS 2 sources imported. Now run scripts/build.sh\n'
