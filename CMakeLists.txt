cmake_minimum_required(VERSION 3.0.2)
project(rqt_lcm_logger)
find_package(catkin REQUIRED COMPONENTS
  rospy
  rqt_gui
  rqt_gui_py
)


catkin_package()
catkin_python_setup()

install(FILES plugin.xml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(DIRECTORY resource
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(PROGRAMS scripts/rqt_lcm_logger
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)