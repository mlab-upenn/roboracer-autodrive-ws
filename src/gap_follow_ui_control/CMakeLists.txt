cmake_minimum_required(VERSION 3.8)
project(gap_follow_ui_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(roboracer_interfaces REQUIRED)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

# CPP
include_directories(include)

add_executable(gap_follow_ui_control src/gap_follow_ui_control_node.cpp)
ament_target_dependencies(gap_follow_ui_control rclcpp ament_index_cpp)

install(TARGETS
  gap_follow_ui_control
  DESTINATION lib/${PROJECT_NAME}
)

# Python
ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/gap_follow_ui_control_node.py
  scripts/gap_follow_get_params.py
  DESTINATION lib/${PROJECT_NAME}
)

# Launch
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

# Using Config Files
install(DIRECTORY
  config/
  DESTINATION share/${PROJECT_NAME}/config
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
