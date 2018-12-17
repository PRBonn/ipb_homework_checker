add_subdirectory(/usr/src/gtest
                 ${PROJECT_BINARY_DIR}/gtest)
include(CTest) # Include testing cmake package.

add_executable(my_tests test_dummy.cpp)
target_link_libraries(my_tests gtest gtest_main)

add_test(my_tests ${PROJECT_BINARY_DIR}/tests/my_tests)
