# MoveIt 与 ros2_control 控制器配置的关系

本文说明下面两个配置文件的职责和关系：

- `src/abb_irb1200_gripper_description/config/controllers.yaml`
- `src/abb_irb1200_gripper_moveit_config/config/moveit_controllers.yaml`

两个文件描述的是同一批控制器，但服务于不同系统：

- `controllers.yaml` 交给 **ros2_control**，负责真正创建、配置和运行控制器。
- `moveit_controllers.yaml` 交给 **MoveIt**，告诉 MoveIt 有哪些控制器，以及如何向它们发送轨迹。

## 1. 职责对比

| 内容 | `controllers.yaml` | `moveit_controllers.yaml` |
|---|---|---|
| 使用者 | ros2_control 的 `controller_manager` | MoveIt 控制器管理器 |
| 主要用途 | 创建并配置控制器 | 查找和调用控制器 |
| 是否真正启动控制器 | 是，由 launch 中的 spawner 加载和激活 | 否 |
| 是否指定硬件接口 | 是 | 否 |
| 关节列表的含义 | 控制器实际控制的关节 | MoveIt 可以交给该控制器的轨迹关节 |
| Action 信息 | 由控制器插件提供 | 声明 Action 类型和命名空间 |

可以将它们理解为：

```text
controllers.yaml
= 控制器的服务端配置

moveit_controllers.yaml
= MoveIt 的客户端通讯录
```

## 2. `controllers.yaml`：ros2_control 侧

该文件首先在 `controller_manager` 下声明控制器插件类型：

```yaml
controller_manager:
  ros__parameters:
    arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController
    gripper_controller:
      type: joint_trajectory_controller/JointTrajectoryController
```

这让 `controller_manager` 加载两个 `JointTrajectoryController`。

机械臂控制器配置为：

```yaml
arm_controller:
  ros__parameters:
    joints: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6]
    command_interfaces: [position]
    state_interfaces: [position, velocity]
```

含义如下：

- `arm_controller` 实际控制六个机械臂关节。
- 控制器向硬件的 `position` 命令接口写入目标值。
- 控制器从硬件读取 `position` 和 `velocity` 状态。

夹爪控制器配置为：

```yaml
gripper_controller:
  ros__parameters:
    joints: [left_finger_joint]
    command_interfaces: [position]
    state_interfaces: [position, velocity]
```

控制器被加载并激活以后，会提供以下 Action：

```text
/arm_controller/follow_joint_trajectory
/gripper_controller/follow_joint_trajectory
```

注意：配置文件描述如何创建控制器，实际加载和激活操作由 `sim_bringup.launch.py` 等 launch 文件中的 `spawner` 完成。

## 3. `moveit_controllers.yaml`：MoveIt 侧

该文件告诉 MoveIt 可以使用哪些控制器：

```yaml
moveit_simple_controller_manager:
  controller_names: [arm_controller, gripper_controller]
```

机械臂控制器的 MoveIt 配置为：

```yaml
arm_controller:
  type: FollowJointTrajectory
  action_ns: follow_joint_trajectory
  default: true
  joints: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6]
```

MoveIt 根据“控制器名称 + Action 命名空间”得到完整地址：

```text
arm_controller + follow_joint_trajectory
                    ↓
/arm_controller/follow_joint_trajectory
```

夹爪同理，对应：

```text
/gripper_controller/follow_joint_trajectory
```

这个配置文件不会创建控制器或 Action 服务，只会告诉 MoveIt 应该到哪里寻找它们。

## 4. 两个文件如何连接

以机械臂控制器为例：

```text
controllers.yaml
创建并配置 arm_controller
             │
             │ 对外提供 Action
             ▼
/arm_controller/follow_joint_trajectory
             ▲
             │ 根据名称和 action_ns 查找
             │
moveit_controllers.yaml
告诉 MoveIt 使用 arm_controller
```

一次轨迹规划与执行的完整流程是：

```text
MoveIt 规划出轨迹
        │
        ▼
读取 moveit_controllers.yaml
        │
        ▼
选择 arm_controller
        │
        ▼
发送 FollowJointTrajectory Goal
        │
        ▼
ros2_control 的 arm_controller 接收轨迹
        │
        ▼
向六个关节的 position command interface 写入命令
        │
        ▼
Mock Hardware / Gazebo / ABB 真机
```

## 5. 两边必须保持一致的内容

### 5.1 控制器名称

两个文件中的名称必须一致：

```yaml
arm_controller
gripper_controller
```

如果 ros2_control 创建的是 `arm_controller`，而 MoveIt 配置写成 `robot_arm_controller`，MoveIt 就会尝试访问不存在的地址：

```text
/robot_arm_controller/follow_joint_trajectory
```

### 5.2 关节名称和关节集合

`arm_controller` 在两个文件中都应该覆盖：

```text
joint_1, joint_2, joint_3, joint_4, joint_5, joint_6
```

如果两边不一致，可能出现：

- MoveIt 找不到能够覆盖轨迹全部关节的控制器。
- ros2_control 控制器拒绝收到的轨迹。
- 控制器报告轨迹中的关节名称不符合预期。

### 5.3 Action 名称

MoveIt 中的：

```yaml
action_ns: follow_joint_trajectory
```

必须和 `JointTrajectoryController` 实际提供的 Action 名称一致。

### 5.4 控制器类型

ros2_control 侧使用：

```text
joint_trajectory_controller/JointTrajectoryController
```

MoveIt 侧对应配置为：

```yaml
type: FollowJointTrajectory
```

两者兼容：前者提供 `control_msgs/action/FollowJointTrajectory` Action，后者通过该 Action 发送轨迹。

## 6. 为什么需要两个文件

两个文件不能简单合并，因为它们属于两个相互独立的框架。

`controllers.yaml` 关心：

- 要加载什么控制器插件？
- 控制器控制哪些关节？
- 使用哪些命令接口和状态接口？
- 控制循环及状态发布频率是多少？

`moveit_controllers.yaml` 关心：

- MoveIt 可以使用哪些控制器？
- 控制器的 Action 地址是什么？
- 每个控制器能够执行哪些关节的轨迹？
- 默认使用哪个控制器？

虽然控制器名称和关节列表存在重复，但这些重复构成了 MoveIt 与 ros2_control 之间的接口约定。

## 总结

`controllers.yaml` 真正提供控制服务，`moveit_controllers.yaml` 则告诉 MoveIt 如何找到并调用该服务。

