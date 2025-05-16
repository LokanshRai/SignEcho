# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(hello_world)

target_include_directories(app PRIVATE includes)

target_sources(app PRIVATE src/main.c)
target_sources(app PRIVATE src/imu.c)
target_sources(app PRIVATE src/emg.c)
target_sources(app PRIVATE src/ble.c)
target_sources(app PRIVATE src/packetBuilder.c)