#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/humble/setup.bash
cd "$ROOT"
colcon build --symlink-install
printf '\nBuild complete. Run:\n  source %s/install/setup.bash\n' "$ROOT"
