# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a ROS2 package (`bobble_localization`) that provides EKF-based state estimation for the BobbleBot using `robot_localization`. It fuses wheel odometry and IMU data to produce a filtered pose estimate and publishes the authoritative `odom` → `bobble_chassis_link` TF transform.

This is a configuration-only package — no custom source code, just config files and a launch file wrapping the `robot_localization` EKF node.

## Build Commands

```bash
# Build the package (run from workspace root ~/Projects/ros_ws)
colcon build --packages-select bobble_localization

# Build entire workspace
colcon build

# Source the workspace
source install/setup.bash
```

## Launch Commands

```bash
# Launch EKF localization node
ros2 launch bobble_localization localization.launch.py

# Launch with custom namespace
ros2 launch bobble_localization localization.launch.py namespace:=robot1

# Launch with real hardware (disable sim time)
ros2 launch bobble_localization localization.launch.py use_sim_time:=false
```

### Launch Parameters (`localization.launch.py`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `use_sim_time` | `true` | Use simulated time (set `false` for real hardware) |
| `namespace` | `bobble` | Robot namespace |

### What the Launch File Does
- Starts the `ekf_node` from `robot_localization` as `ekf_filter_node`
- Loads parameters from `config/ekf.yaml`
- Remaps output topic: `odometry/filtered` → `odom/filtered`
- Runs in the configured namespace (default: `/bobble`)

## Architecture

### EKF Configuration (`config/ekf.yaml`)

**Filter parameters:**
- Frequency: 50 Hz
- 3D mode (`two_d_mode: false`) — important for a self-balancing robot that tilts
- `publish_tf: true` — this node owns the `odom` → `bobble_chassis_link` TF

**Frame IDs:**
- `odom_frame`: `odom`
- `base_link_frame`: `bobble_chassis_link`
- `world_frame`: `odom`

### Sensor Fusion Strategy

The EKF fuses two sensor sources:

**1. Wheel Odometry (`odom0`: `/bobble_controller/odom`)**
- Fuses: linear velocity X only (`vx`)
- `odom0_differential: false` — uses raw measurements
- Source: diff_drive_controller in `bobble_description`

**2. IMU (`imu0`: `/bobble/imu`)**
- Fuses: orientation (roll, pitch, yaw) + angular velocity (all axes)
- `imu0_differential: false` — uses raw measurements
- Source: BNO055 IMU Gazebo plugin in `bobble_description`

### State Vector (15 elements)
```
[x, y, z, roll, pitch, yaw, vx, vy, vz, vroll, vpitch, vyaw, ax, ay, az]

odom0 fuses:  [ -  -  -   -     -     -   vx  -   -    -      -      -    -   -   - ]
imu0  fuses:  [ -  -  -  roll  pitch  yaw  -   -   -  vroll  vpitch vyaw  -   -   - ]
```

### Why This Package Exists

The diff_drive_controller in `bobble_description` has `enable_odom_tf: false`. This is intentional — the EKF here produces a **fused** `odom` → `base_link` TF that combines wheel encoders with IMU data, which is more accurate than raw wheel odometry alone. This matters because:

- **Wheel slip**: Encoders can't detect when wheels lose traction
- **Self-balancing**: The robot continuously tilts; the IMU provides accurate pitch/roll
- **Yaw drift**: IMU gyroscope corrects for accumulated heading error from encoders
- **No TF conflicts**: Only one node publishes each TF transform

### Key Topics
| Topic | Direction | Description |
|-------|-----------|-------------|
| `/bobble_controller/odom` | Input | Raw wheel odometry from diff drive controller |
| `/bobble/imu` | Input | IMU data from Gazebo BNO055 plugin |
| `/bobble/odom/filtered` | Output | Fused odometry estimate |
| `odom` → `bobble_chassis_link` | Output (TF) | Fused transform |

### Dependencies
- `robot_localization` — provides the EKF node
- `launch`, `launch_ros` — launch system

### Related Packages
- **`bobble_description`** (in same workspace) — robot URDF, controllers, and Gazebo simulation; provides the sensor data this package fuses

IMPORTANT: Once you set yourself some todos, you should complete them without stopping,
*unless*
 you have some particular
*reason*
 to stop (e.g. you need to ask a question, you need feedback / input, etc.) If you do stop before finishing all todos, you MUST state the reason why you're stopping. We'll call this the "no-stop" rule. If you stop before finishing todos, and don't give any reason why you've stopped, I'll be very disappointed, and I'll ask you why you didn't follow the "no-stop rule."
