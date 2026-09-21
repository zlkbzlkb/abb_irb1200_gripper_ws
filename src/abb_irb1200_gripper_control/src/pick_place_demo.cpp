#include <chrono>
#include <memory>
#include <thread>
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "moveit/move_group_interface/move_group_interface.h"
#include "control_msgs/action/follow_joint_trajectory.hpp"

using namespace std::chrono_literals;
using FollowJT = control_msgs::action::FollowJointTrajectory;

class GripperClient {
public:
  explicit GripperClient(const rclcpp::Node::SharedPtr& node)
  : node_(node), client_(rclcpp_action::create_client<FollowJT>(node_, "/gripper_controller/follow_joint_trajectory")) {}

  bool command(double position) {
    if (!client_->wait_for_action_server(5s)) {
      RCLCPP_ERROR(node_->get_logger(), "Gripper action server not available"); return false;
    }
    FollowJT::Goal goal;
    goal.trajectory.joint_names = {"left_finger_joint"};
    trajectory_msgs::msg::JointTrajectoryPoint p;
    p.positions = {position};
    p.time_from_start = rclcpp::Duration(1s);
    goal.trajectory.points = {p};
    client_->async_send_goal(goal);
    std::this_thread::sleep_for(1200ms);
    return true;
  }
private:
  rclcpp::Node::SharedPtr node_;
  rclcpp_action::Client<FollowJT>::SharedPtr client_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("abb_pick_place_demo", rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));
  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor](){ executor.spin(); });

  moveit::planning_interface::MoveGroupInterface arm(node, "manipulator");
  arm.setMaxVelocityScalingFactor(0.15);
  arm.setMaxAccelerationScalingFactor(0.10);
  GripperClient gripper(node);

  RCLCPP_INFO(node->get_logger(), "Opening gripper...");
  gripper.command(0.035);

  std::vector<double> ready{0.0, -0.55, 0.75, 0.0, 0.55, 0.0};
  arm.setJointValueTarget(ready);
  moveit::planning_interface::MoveGroupInterface::Plan plan;
  if (arm.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS) arm.execute(plan);

  geometry_msgs::msg::Pose target = arm.getCurrentPose().pose;
  target.position.z -= 0.08;
  arm.setPoseTarget(target, "tool0");
  if (arm.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS) arm.execute(plan);

  RCLCPP_INFO(node->get_logger(), "Closing gripper...");
  gripper.command(0.0);
  target.position.z += 0.12;
  arm.setPoseTarget(target, "tool0");
  if (arm.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS) arm.execute(plan);

  rclcpp::shutdown();
  if (spinner.joinable()) spinner.join();
  return 0;
}
