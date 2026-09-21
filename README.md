# ABB IRB1200 + Gripper ROS 2 Humble Demo Workspace

This workspace is a teaching/reference project for Ubuntu 22.04 + ROS 2 Humble. It demonstrates:

- a six-axis ABB IRB1200-class arm model with a two-finger gripper;
- ros2_control with `joint_state_broadcaster`, `joint_trajectory_controller`, and mock hardware;
- MoveIt 2 motion planning;
- a C++ pick/lift example;
- a Gazebo Classic launch path;
- a **real ABB integration path using `abb_ros2` / EGM**, rather than pretending the local demo model is a production ABB driver;
- a migration guide for replacing ABB with another robot.

> Safety: the included primitive URDF is for teaching/simulation only. Do not use its dimensions, inertias, joint limits, or collision geometry for a production robot. For real ABB use the vendor/community support description and validate the controller, EGM/RWS configuration, safety zones, payload, tool data and speed limits on the robot side.

## 1. Dependencies

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y \
  ros-humble-moveit \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control \
  ros-humble-xacro ros-humble-joint-state-publisher-gui
```

## 2. Build

```bash
cd ~/abb_irb1200_gripper_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## 3. Check robot model

```bash
ros2 launch abb_irb1200_gripper_description view.launch.py
```

## 4. ros2_control mock-hardware simulation

Terminal 1:

```bash
ros2 launch abb_irb1200_gripper_control sim_bringup.launch.py
```

Verify:

```bash
ros2 control list_controllers
ros2 topic echo /joint_states
```

Expected controllers: `joint_state_broadcaster`, `arm_controller`, `gripper_controller`.

## 5. Start MoveIt 2

Terminal 2:

```bash
source ~/abb_irb1200_gripper_ws/install/setup.bash
ros2 launch abb_irb1200_gripper_moveit_config moveit.launch.py
```

In RViz add/use MotionPlanning, group `manipulator`, and plan to a goal.

## 6. Run the C++ example

Terminal 3:

```bash
source ~/abb_irb1200_gripper_ws/install/setup.bash
ros2 run abb_irb1200_gripper_control pick_place_demo
```

The example opens the gripper, moves to a ready configuration, moves tool0 down, closes the gripper, then lifts.

## 7. Gazebo Classic

```bash
ros2 launch abb_irb1200_gripper_control gazebo_bringup.launch.py
```

Then start MoveIt in another terminal. Gazebo Classic is used because it is the common simulator path on ROS 2 Humble/Ubuntu 22.04. If your machine uses modern Gazebo (`gz`), replace `gazebo_ros2_control` with `gz_ros2_control` and update the launch/plugin blocks.

## 8. Real ABB robot

For an actual ABB IRB1200, use the `abb_ros2` stack and the real robot description/config, not the primitive model in this workspace.

Typical source install:

```bash
cd ~/abb_irb1200_gripper_ws/src
git clone -b humble https://github.com/PickNikRobotics/abb_ros2.git
cd abb_ros2
vcs import < abb.repos
cd ~/abb_irb1200_gripper_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Then, after RobotWare/EGM/RWS/networking and safety configuration is complete:

```bash
ros2 launch abb_irb1200_gripper_control real_abb_bringup.launch.py \
  rws_ip:=192.168.125.1 rws_port:=80
```

The ABB arm side uses `abb_hardware_interface/ABBSystemHardware` through `abb_ros2`. The physical gripper is intentionally separate: configure the gripper's real ROS 2 driver/controller and expose a MoveIt-compatible gripper controller/action.

Do not execute motion on a physical robot until you have tested the exact same configuration in RobotStudio/fake hardware, established an E-stop/safe operating mode, verified TCP/tool load, confirmed joint limits, and started at very low speed.

See `ROBOT_REPLACEMENT_GUIDE.md` for replacing ABB with another robot.

## 9. Helper scripts

```bash
cd ~/abb_irb1200_gripper_ws
./scripts/check_install.sh
./scripts/install_deps.sh
./scripts/build.sh
```

To import the upstream ABB ROS 2 Humble sources for real-robot/RobotStudio work:

```bash
./scripts/get_abb_ros2_humble.sh
./scripts/build.sh
```

## 10. Recommended learning/test order

1. `view.launch.py`: understand URDF/joints.
2. `sim_bringup.launch.py`: understand controller_manager and ros2_control.
3. `moveit.launch.py`: understand planning/execution.
4. `pick_place_demo`: understand the C++ MoveIt API.
5. `gazebo_bringup.launch.py`: add physics.
6. Upstream `abb_ros2` + RobotStudio.
7. Only then connect a physical ABB at low speed with the manufacturer's safety procedures.
