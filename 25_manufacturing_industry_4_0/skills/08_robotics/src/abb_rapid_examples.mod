MODULE RoboticAssemblyPrograms
    !
    ! Comprehensive ABB RAPID Programming Examples
    ! Industrial Robotics Applications
    ! Compatible: IRB 1200, IRB 6700, IRB 14000, and other ABB 6-axis robots
    !

    ! =====================================================================
    ! SECTION 1: BASIC MOTION AND I/O EXAMPLES
    ! =====================================================================

    PROC BasicMotionExample()
        !
        ! Demonstrates fundamental motion instructions
        ! MoveJ: Joint motion (fastest point-to-point)
        ! MoveL: Linear motion (straight line path)
        ! MoveC: Circular motion (arc path)
        !

        ! Move to home position via joint interpolation
        MoveJ home_pos, v100, z50, tool0;

        ! Move to target position with linear motion
        ! Maintains tool orientation
        MoveL target_pos, v100, z50, tool0;

        ! Move in circular arc with intermediate point
        MoveC mid_point, end_point, v80, z25, tool0;

        ! Return to home
        MoveJ home_pos, v100, z50, tool0;

    ENDPROC

    PROC DigitalIOExample()
        !
        ! Demonstrates digital input/output operations
        ! Useful for gripper control, sensor monitoring
        !

        ! Set digital output (activate gripper)
        SetDO gripper_open, 1;
        WaitTime 0.5;

        ! Set digital output (close gripper)
        SetDO gripper_open, 0;
        WaitTime 1.0;

        ! Wait for input signal (part ready)
        WaitDI sensor_part_ready, 1;

        ! Conditional logic based on input
        IF (DInput(sensor_part_ready) = 1) THEN
            SetDO indicator_light, 1;
        ELSE
            SetDO indicator_light, 0;
        ENDIF

    ENDPROC

    PROC AnalogIOExample()
        !
        ! Demonstrates analog input/output operations
        ! Useful for pressure sensors, valve control
        !

        ! Set analog output for pressure valve
        SetAO pressure_control, 50.0;

        ! Read analog input (pressure sensor)
        VAR num current_pressure;
        current_pressure := AInput(pressure_sensor);

        ! Conditional valve control based on pressure
        IF current_pressure > 80.0 THEN
            SetAO pressure_control, 30.0;  ! Reduce pressure
        ELSEIF current_pressure < 40.0 THEN
            SetAO pressure_control, 70.0;  ! Increase pressure
        ENDIF

    ENDPROC

    ! =====================================================================
    ! SECTION 2: PICK AND PLACE APPLICATION
    ! =====================================================================

    PROC PickAndPlace()
        !
        ! Complete pick and place cycle
        ! Application: Material handling, machine tending
        ! Safety: Includes collision avoidance and error checking
        !

        VAR num cycle_count := 0;
        VAR num max_cycles := 1000;

        ! Initialize
        CONNECT handler_name TO emergency_stop_signal;
        MoveJ home_pos, v100, z50, tool0;
        SetDO system_ready_light, 1;

        WHILE cycle_count < max_cycles DO

            ! Wait for part ready signal from feeder
            WaitDI feeder_signal, 1, 10.0;  ! 10 second timeout

            ! Move to approach position above part
            MoveJ approach_pos, v100, z50, tool0;

            ! Move linearly to grasp position
            MoveL grasp_pos, v100, z25, tool0;

            ! Close gripper
            SetDO gripper_close, 1;
            WaitTime 0.5;  ! Allow gripper to fully close

            ! Verify grasp with sensor feedback
            IF (DInput(gripper_feedback) = 1) THEN
                ! Grasp successful, retract
                MoveL retract_pos, v100, z25, tool0;

                ! Move to intermediate waypoint (avoid obstacles)
                MoveJ transfer_pos, v100, z50, tool0;

                ! Move to placement position
                MoveJ placement_approach, v100, z50, tool0;
                MoveL placement_pos, v100, z25, tool0;

                ! Release gripper
                SetDO gripper_close, 0;
                WaitTime 0.3;

                ! Retract to safe position
                MoveL placement_retract, v100, z25, tool0;

                ! Return to home
                MoveJ home_pos, v100, z50, tool0;

                ! Increment cycle counter
                cycle_count := cycle_count + 1;
                SetAO cycle_counter_output, num_to_voltage(cycle_count);

            ELSE
                ! Grasp failed - error handling
                SetDO alarm_light, 1;
                WaitTime 0.5;
                SetDO alarm_light, 0;

                ! Attempt to recover
                MoveJ home_pos, v100, z50, tool0;
                WaitTime 2.0;

            ENDIF

        ENDWHILE

        ! Program complete
        MoveJ home_pos, v100, z50, tool0;
        SetDO system_ready_light, 0;
        SetDO gripper_close, 0;

    ENDPROC

    ! =====================================================================
    ! SECTION 3: WELDING APPLICATION
    ! =====================================================================

    PROC ArcWeldingSequence()
        !
        ! Arc welding with torch control
        ! Application: Robotic welding of joints
        ! Requires: Welding gun mounted on wrist, Welding power supply
        !

        VAR bool weld_complete;

        ! Move to initial position
        MoveJ weld_start_approach, v80, z50, tool_welder;

        ! Approach seam with controlled speed
        MoveL weld_start_pos, v50, z10, tool_welder;

        ! Enable wire feed and arc initiation
        SetDO weld_torch_enable, 1;
        SetAO weld_current_control, 250.0;  ! Set welding current (amps)
        WaitTime 0.5;

        ! Linear weld along seam
        ! Traverse along seam path with constant speed
        MoveL weld_mid_pos1, v30, z5, tool_welder;
        MoveL weld_mid_pos2, v30, z5, tool_welder;
        MoveL weld_end_pos, v30, z5, tool_welder;

        ! Disable welding
        SetDO weld_torch_enable, 0;
        SetAO weld_current_control, 0.0;
        WaitTime 1.0;  ! Allow arc to cool

        ! Retract from part
        MoveL weld_end_retract, v60, z20, tool_welder;
        MoveJ home_pos, v100, z50, tool_welder;

    ENDPROC

    ! =====================================================================
    ! SECTION 4: MACHINE TENDING APPLICATION
    ! =====================================================================

    PROC MachineTending()
        !
        ! Complete machine tending sequence
        ! Application: CNC machine loading/unloading
        ! Synchronization with machine spindle
        !

        VAR num part_counter := 0;

        WHILE TRUE DO

            ! Wait for machine ready signal
            WaitDI machine_ready, 1;

            ! Approach machine chuck
            MoveJ machine_approach, v100, z50, tool0;

            ! Open gripper before loading
            SetDO gripper_open_cmd, 1;
            WaitTime 0.3;

            ! Move to part staging area
            MoveJ staging_position, v100, z50, tool0;

            ! Load new part from feeder
            MoveL feeder_pick_pos, v100, z20, tool0;
            SetDO gripper_open_cmd, 0;  ! Close gripper on part
            WaitTime 0.5;

            ! Move part to machine
            MoveL machine_load_pos, v100, z20, tool0;

            ! Release part in chuck
            SetDO gripper_open_cmd, 1;
            WaitTime 0.5;

            ! Retract from machine
            MoveL machine_retract, v100, z50, tool0;

            ! Send machine cycle start command
            SetDO machine_start_signal, 1;
            WaitTime 0.1;
            SetDO machine_start_signal, 0;

            ! Wait for cycle complete
            WaitDI machine_cycle_complete, 1, 30.0;  ! 30 second timeout

            ! Approach machine for unload
            MoveJ machine_approach, v100, z50, tool0;

            ! Unload finished part
            MoveL machine_unload_pos, v100, z20, tool0;
            SetDO gripper_open_cmd, 0;  ! Close gripper
            WaitTime 0.5;

            ! Move to output conveyor
            MoveL output_position, v100, z50, tool0;
            SetDO gripper_open_cmd, 1;  ! Release part
            WaitTime 0.5;

            ! Return to home
            MoveJ home_pos, v100, z50, tool0;

            ! Increment counter
            part_counter := part_counter + 1;

        ENDWHILE

    ENDPROC

    ! =====================================================================
    ! SECTION 5: VISION-GUIDED ASSEMBLY
    ! =====================================================================

    PROC VisionGuidedAssembly()
        !
        ! Assembly with vision system feedback
        ! Application: Precise component placement
        ! Requires: Vision system integrated with controller
        !

        VAR num vis_x, vis_y, vis_angle;
        VAR pose detected_part_pose;

        ! Move to vision scan position
        MoveJ vision_scan_pos, v100, z50, tool0;

        ! Trigger vision capture
        SetDO vision_trigger, 1;
        WaitTime 0.1;
        SetDO vision_trigger, 0;

        ! Wait for vision data
        WaitDI vision_data_ready, 1, 5.0;

        ! Read vision coordinates (from external vision system)
        ! In real implementation, would receive from separate vision controller
        vis_x := 150.0;      ! Example X coordinate (mm)
        vis_y := 200.0;      ! Example Y coordinate (mm)
        vis_angle := 45.0;   ! Example part angle (degrees)

        ! Calculate grasp position based on vision
        VAR pose grasp_offset := [[vis_x, vis_y, -50], [0, 0, vis_angle, 0]];

        ! Move to approach position
        MoveJ approach_from_vision, v100, z50, tool0;

        ! Move to vision-guided grasp position
        MoveL grasp_offset, v100, z25, tool0;

        ! Grasp part
        SetDO gripper_close, 1;
        WaitTime 0.5;

        ! Retract and place
        MoveL retract_pos, v100, z25, tool0;
        MoveJ assembly_approach, v100, z50, tool0;
        MoveL assembly_pos, v100, z25, tool0;

        ! Release
        SetDO gripper_close, 0;
        WaitTime 0.3;

        ! Return to home
        MoveL retract_pos, v100, z25, tool0;
        MoveJ home_pos, v100, z50, tool0;

    ENDPROC

    ! =====================================================================
    ! SECTION 6: ERROR HANDLING AND RECOVERY
    ! =====================================================================

    PROC ErrorHandlingExample()
        !
        ! Demonstrates error detection and recovery
        ! Safety-critical operations
        !

        ON ERROR
            ! Error handler triggered
            IF (ERRNO = ERR_ROBLIMIT) THEN
                ! Robot limit violation
                TPWrite "Robot limit reached";
                ! Move away from limit
                MoveJ home_pos, v100, z50, tool0;

            ELSEIF (ERRNO = ERR_COLLFAULT) THEN
                ! Collision detected
                TPWrite "Collision fault";
                ! Emergency retract
                MoveJ safe_retract_pos, v500, z50, tool0;

            ELSEIF (ERRNO = ERR_IO) THEN
                ! I/O error
                TPWrite "I/O device error";

            ELSE
                ! Unknown error
                TPWrite "Unknown error: " + ValtoStr(ERRNO);

            ENDIF

            ! Log error for diagnostics
            LogErrorEvent(ERRNO);

        UNDO

        ! Protected code (will trigger error handler if error occurs)
        MoveL target_position, v100, z50, tool0;

    ENDPROC

    PROC InterruptHandlerExample()
        !
        ! Interrupt handling for asynchronous events
        ! Useful for emergency stop or task abort
        !

        ! Define interrupt handler
        INTERRUPT handler_emergency_stop

            ! Immediate actions
            StopMove;
            SetDO all_outputs, 0;  ! Kill all outputs
            TPWrite "Emergency Stop Activated";
            ! Program halts - requires manual restart

        ENDINTERRUPT

        ! Attach handler to signal
        CONNECT handler_emergency_stop TO emergency_signal;
        ! Now if emergency_signal triggers, handler runs immediately

    ENDPROC

    ! =====================================================================
    ! SECTION 7: DATA LOGGING AND TRACEABILITY
    ! =====================================================================

    PROC ProductionLogging()
        !
        ! Log production data for quality tracking
        ! Captures: Cycle number, timestamp, quality metrics
        !

        VAR num cycle_number := 0;
        VAR num quality_score := 0;
        VAR string timestamp_str;
        VAR file log_file;

        ! Open log file
        OPEN_FILE log_file, "/memotx/production_log.txt", "a";

        WHILE cycle_number < 1000 DO

            ! Perform assembly task
            ! ... (assembly code here) ...

            ! Get current time (requires system integration)
            ! timestamp_str := GetCurrentTime();

            ! Evaluate quality (example metrics)
            quality_score := 95 + (cycle_number MOD 5);

            ! Log to file
            WRITE log_file, "Cycle: " + ValtoStr(cycle_number);
            WRITE log_file, "Quality: " + ValtoStr(quality_score);
            WRITE log_file, "Status: PASS";
            WRITE log_file, "---";

            ! Also send to network monitoring
            SetAO production_counter, VAL_TO_ANALOG(cycle_number);

            cycle_number := cycle_number + 1;

        ENDWHILE

        CLOSE_FILE log_file;

    ENDPROC

    ! =====================================================================
    ! SECTION 8: ADVANCED MOTION - BLENDING AND SMOOTH PATHS
    ! =====================================================================

    PROC SmoothPathMotion()
        !
        ! Demonstrates path blending for smooth motion
        ! Reduces cycle time while maintaining smoothness
        !

        ! Small zone for sharp corners
        MoveJ pos1, v100, z5, tool0;      ! Tight stop at pos1
        MoveJ pos2, v100, z5, tool0;      ! Tight stop at pos2

        ! OR

        ! Larger zone for blending (faster, smoother)
        MoveJ pos1, v100, z100, tool0;    ! Loose zone for blending
        MoveJ pos2, v100, z100, tool0;    ! Robot blends between points

        ! This second approach is faster because robot doesn't fully stop

    ENDPROC

    ! =====================================================================
    ! SECTION 9: SYNCHRONIZATION WITH EXTERNAL EQUIPMENT
    ! =====================================================================

    PROC SynchronizedOperation()
        !
        ! Coordinate robot with external equipment
        ! Example: Conveyor positioning, machine synchronization
        !

        VAR bool conveyor_running := FALSE;

        ! Start conveyor
        SetDO conveyor_enable, 1;
        conveyor_running := TRUE;

        ! Move robot to pick position
        MoveJ pick_position, v100, z50, tool0;

        ! Wait for conveyor to position part
        WHILE (DInput(part_positioned) = 0) DO
            WaitTime 0.1;
        ENDWHILE

        ! Pick part
        MoveL pick_grasp, v100, z25, tool0;
        SetDO gripper_close, 1;
        WaitTime 0.5;

        ! Retract while conveyor continues
        MoveL pick_retract, v100, z25, tool0;

        ! Place part on assembly fixture (which is also controlled)
        MoveJ assembly_position, v100, z50, tool0;
        MoveL assembly_place, v100, z25, tool0;
        SetDO gripper_close, 0;
        WaitTime 0.3;

        ! Send signal to fixture to clamp part
        SetDO fixture_clamp, 1;
        WaitTime 1.0;  ! Wait for clamping

        ! Retract
        MoveL assembly_retract, v100, z25, tool0;
        MoveJ home_pos, v100, z50, tool0;

        ! Stop conveyor
        SetDO conveyor_enable, 0;
        conveyor_running := FALSE;

    ENDPROC

    ! =====================================================================
    ! SECTION 10: SAFETY OPERATIONS AND TEACH MODE
    ! =====================================================================

    PROC TeachModeExample()
        !
        ! Safe teaching procedure
        ! MUST enforce: 0.25 m/s speed limit in teach mode
        !

        VAR speeddata teach_speed := [0.25, 45, 9, 45];  ! 0.25 m/s limit per ISO 10218

        TPWrite "Entering Teach Mode";
        TPWrite "Move robot with teach pendant";
        TPWrite "Speed limited to 0.25 m/s for safety";

        ! Teach point 1
        MoveJ teach_point_1, teach_speed, z50, tool0;
        TPWrite "Record Position 1 (press trigger)";

        ! Teach point 2
        MoveJ teach_point_2, teach_speed, z50, tool0;
        TPWrite "Record Position 2 (press trigger)";

        ! Teach point 3
        MoveJ teach_point_3, teach_speed, z50, tool0;
        TPWrite "Record Position 3 (press trigger)";

        TPWrite "Teaching complete - returning to normal speed";
        MoveJ home_pos, v100, z50, tool0;

    ENDPROC

    PROC SafeStartupShutdown()
        !
        ! Safe startup and shutdown procedures
        !

        ! ===== STARTUP =====
        TPWrite "System Startup";

        ! Clear any residual signals
        SetDO gripper_close, 0;
        SetDO gripper_open, 0;
        SetAO all_analog, 0.0;

        ! Move to home position
        MoveJ home_pos, v100, z50, tool0;

        ! Verify all systems operational
        IF (DInput(system_ok) = 1) THEN
            TPWrite "All systems ready";
            SetDO system_ready_light, 1;
        ELSE
            TPWrite "System fault detected - contact maintenance";
            STOP;
        ENDIF

        ! ===== NORMAL OPERATION =====
        ! ... main program here ...

        ! ===== SHUTDOWN =====
        TPWrite "System Shutdown";

        ! Return to safe position
        MoveJ home_pos, v100, z50, tool0;

        ! Kill all outputs
        SetDO gripper_close, 0;
        SetDO gripper_open, 0;
        SetAO all_analog, 0.0;

        ! Disable system
        SetDO system_ready_light, 0;
        TPWrite "System shutdown complete";

    ENDPROC

    ! =====================================================================
    ! HELPER PROCEDURES AND UTILITIES
    ! =====================================================================

    PROC LogErrorEvent(VAR errnum error_code)
        !
        ! Log error event for diagnostics
        !
        VAR string error_message;

        IF error_code = ERR_ROBLIMIT THEN
            error_message := "Robot limit exceeded";
        ELSEIF error_code = ERR_COLLFAULT THEN
            error_message := "Collision fault";
        ELSE
            error_message := "Error code: " + ValtoStr(error_code);
        ENDIF

        TPWrite "ERROR: " + error_message;

    ENDPROC

    FUNC num ValtoStr(VAR num value)
        !
        ! Convert number to string for logging
        !
        RETURN value;
    ENDFUNC

    FUNC num NUM_TO_VOLTAGE(VAR num count)
        !
        ! Convert count to 0-10V output
        ! Used for analog monitoring
        !
        VAR num voltage;
        voltage := (count MOD 1000) / 100;  ! Scale 0-1000 to 0-10V
        RETURN voltage;
    ENDFUNC

    ! =====================================================================
    ! MAIN PROGRAM ENTRY POINT
    ! =====================================================================

    PROC main()
        !
        ! Main program - select which example to run
        !
        VAR num program_select := 2;  ! Change to run different examples

        ! Move to safe home position
        MoveJ home_pos, v100, z50, tool0;

        SELECT program_select OF

            CASE 1:
                TPWrite "Running: Basic Motion";
                BasicMotionExample;

            CASE 2:
                TPWrite "Running: Pick and Place";
                PickAndPlace;

            CASE 3:
                TPWrite "Running: Welding Sequence";
                ArcWeldingSequence;

            CASE 4:
                TPWrite "Running: Machine Tending";
                MachineTending;

            CASE 5:
                TPWrite "Running: Vision-Guided Assembly";
                VisionGuidedAssembly;

            CASE 6:
                TPWrite "Running: Synchronized Operation";
                SynchronizedOperation;

            DEFAULT:
                TPWrite "Unknown program selection";

        ENDSELECT

        ! Return to home at program end
        MoveJ home_pos, v100, z50, tool0;

    ENDPROC

    ! =====================================================================
    ! PERSISTENT VARIABLE DEFINITIONS
    ! =====================================================================

    PERS tooldata tool0 := [
        TRUE,                                    ! Tool mounted (TRUE/FALSE)
        [[0, 0, 100], [1, 0, 0, 0]],           ! TCP offset (100mm Z offset for gripper)
        [1.5, [0, 0, 0.05]],                   ! Load: 1.5kg, COG at 50mm below mount
        [0, 0, 0, 0, 0, 0]                     ! Inertia (typically 0 for simple tools)
    ];

    PERS wobjdata work0 := [
        FALSE,                                  ! Moving object (TRUE/FALSE)
        FALSE,                                  ! Coordinate frame
        [[0, 0, 0], [1, 0, 0, 0]],            ! Frame position
        [[0, 0, 0], [1, 0, 0, 0]]             ! Object frame
    ];

    ! Home position (joint angles in degrees converted to radians)
    PERS robjointpos home_pos := [0, -90, 90, 0, 0, 0];

    ! Approach positions (examples - modify for your application)
    PERS robjointpos approach_pos := [-45, -90, 90, 0, 0, 0];
    PERS robjointpos transfer_pos := [90, -90, 90, 0, 0, 0];

    ! Cartesian positions (X, Y, Z, Rx, Ry, Rz)
    PERS pos grasp_pos := [200, 300, 100, 0, 180, 0];
    PERS pos placement_pos := [400, 200, 100, 0, 180, 0];
    PERS pos retract_pos := [300, 250, 300, 0, 180, 0];

ENDMODULE
