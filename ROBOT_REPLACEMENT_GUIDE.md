# 如何把 ABB IRB1200 + 夹爪替换成其他机械臂

## 一、先理解工程的“固定层”和“可替换层”

推荐保持这些上层接口不变：

```text
你的任务程序 / 视觉 / 强化学习
            ↓
MoveIt 2（manipulator 规划组）
            ↓
arm_controller / follow_joint_trajectory
            ↓
ros2_control
            ↓
Hardware Interface
            ↓
真实机器人
```

替换机器人时，最重要的是替换下方四项：

1. URDF/Xacro（结构、关节、mesh、碰撞模型）；
2. SRDF/MoveIt Config（planning group、end effector、碰撞矩阵）；
3. ros2_control Hardware Interface 和 controllers；
4. 真实机器人驱动。

上层 C++ 任务程序尽量只依赖规划组名 `manipulator`、末端 link 和控制器 action，这样换机器人时修改最少。

## 二、步骤 1：替换 URDF/Xacro

当前文件：

```text
abb_irb1200_gripper_description/urdf/abb_irb1200_gripper.urdf.xacro
```

替换为新机械臂厂商提供的 URDF/Xacro。确认：

```text
base link
6/7 个关节名称
tool0 / flange / ee_link
关节上下限
视觉 mesh
collision mesh
inertial
```

不要只改机器人外观。MoveIt 和 ros2_control 都依赖关节名称完全一致。

例如 ABB：

```text
joint_1 ... joint_6
base_link
tool0
```

换成 UR5e 可能是：

```text
shoulder_pan_joint
shoulder_lift_joint
elbow_joint
wrist_1_joint
wrist_2_joint
wrist_3_joint
base_link
tool0
```

那么 MoveIt、controller YAML、C++ 中所有相关名字都必须同步。

## 三、步骤 2：重新生成 MoveIt Config

推荐使用 MoveIt Setup Assistant：

```bash
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```

完成：

1. 加载新 URDF/Xacro；
2. Generate Self-Collision Matrix；
3. 建立 planning group，建议仍命名为 `manipulator`；
4. Kinematic Chain：新 base link → 新 tool/end-effector link；
5. 添加 End Effector；
6. 设置 Home Pose；
7. 设置 ros2_control；
8. 生成新的 `<robot>_moveit_config`。

保持规划组仍叫 `manipulator` 的好处是，本项目的 C++：

```cpp
MoveGroupInterface arm(node, "manipulator");
```

通常无需修改。

## 四、步骤 3：修改 ros2_control

当前：

```text
arm_controller
  joint_1
  joint_2
  ...
  joint_6
```

换机器人后，把 `controllers.yaml` 的 `joints` 改成新机器人的关节名称。

推荐保持 controller 名仍为：

```text
arm_controller
```

并继续提供：

```text
/arm_controller/follow_joint_trajectory
```

这样 MoveIt 层不需要大改。

## 五、步骤 4：替换 Hardware Interface

仿真/测试：

```xml
<plugin>mock_components/GenericSystem</plugin>
```

真实 ABB：

```xml
<plugin>abb_hardware_interface/ABBSystemHardware</plugin>
```

换机器人时，替换成对应厂商驱动。例如 UR、Franka、xArm、JAKA、AUBO 等，应优先使用该机器人官方或成熟 ROS 2 driver 提供的 ros2_control hardware plugin，而不是自己从零写串口/CAN 控制。

如果厂商驱动不基于 ros2_control，则做一个“适配层”，目标仍然是让 MoveIt 能调用 FollowJointTrajectory 或兼容的控制接口。

## 六、步骤 5：替换夹爪

当前示例只有一个主动关节：

```text
left_finger_joint
```

右侧通过 mimic 关联。

真实夹爪可能是：

- Robotiq 2F-85/2F-140；
- OnRobot RG2；
- DH Robotics；
- 自制 STM32 夹爪。

推荐让夹爪最终对 ROS 2 暴露以下二者之一：

```text
FollowJointTrajectory
```

或：

```text
GripperCommand
```

然后修改 MoveIt 的 `moveit_controllers.yaml` 和 C++ GripperClient。

## 七、步骤 6：修改 C++ 程序中最少的三个地方

当前：

```cpp
MoveGroupInterface arm(node, "manipulator");
arm.setPoseTarget(target, "tool0");
```

新机器人如果保持：

```text
planning group = manipulator
end effector = tool0
```

这部分完全不用改。

否则修改：

```cpp
"manipulator" → 新 planning group
"tool0"        → 新末端 link
```

第三处是夹爪 action：

```text
/gripper_controller/follow_joint_trajectory
```

如果新夹爪不同，再修改它。

## 八、推荐的“机器人无关”工程结构

长期建议把工程改成：

```text
robot_ws/src/
├── manipulation_application/       # 视觉、抓取、任务逻辑；不要放机器人模型
├── robot_description/              # 当前机器人的 URDF
├── robot_moveit_config/            # 当前机器人 MoveIt 配置
├── robot_bringup/                   # 仿真/真机 launch
├── gripper_driver/                  # 夹爪驱动
└── vendor_robot_driver/             # ABB/UR/Franka/... 厂商驱动
```

这样从 ABB 换 UR5e，只替换后 4 个包，`manipulation_application` 基本不动。

## 九、建议的替换验收顺序

每换一种机器人都按下面顺序验证：

```text
1. check_urdf / xacro 能通过
2. RViz 中模型正确
3. /joint_states 正确
4. ros2_control controllers active
5. 单关节低速测试
6. MoveIt Plan 成功
7. Fake hardware Execute 成功
8. 仿真 Execute 成功
9. RobotStudio/厂商虚拟控制器成功
10. 真实机器人低速、空载成功
11. 加夹爪
12. 加视觉与抓取任务
```

不要跳过 5~10 直接让 MoveIt 驱动真实工业机械臂。
