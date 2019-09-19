import threading
import warnings
import util.io as io
import traceback
import sdk.pga as FUS
import multiprocessing
import os


#TODO: Actually record this information somewhere as a log
# class Listener(FUS.FUSListener):
#     def onConnect(self):
#         print("*** CONNECTED ***")
#     def onDisconnect(self, reason):
#         print("*** DISCONNECTED *** (reason=%d)" % reason)
#     def onExecStart (self, execID, mode):
#         print("*** EXEC START *** (id=%d, mode=%d)" % (execID, mode))
#     def onShotResult (self, execID, shot_result):
#         print("*** SHOT RESULT (id=%d) ***" % execID)
#     def onExecResult (self, exec_result):
#         print("*** EXEC RESULT ***")

class FUS_GEN():
    def __init__(self, all_msgs, motor=None, host=None):
        """Initializes connection the IGT FUS Generator and sets up data structures
        for setting up trajectories

        Parameters
        ----------
        host : string
            Host IP address of the IGT FUS generator
        port : int
            Port of the IGT FUS Generator
        timeout_ms: int
            Number of ms to wait before timing out the connection
        """
        self.igt_system = FUS.Generator()#loglevel=FUS.LogLevel.ALL
        self.igt_system.loadConfig("sdk/generator.json")

        self.motor = motor

        self.all_msgs = all_msgs
        
        self.run_thread = None
        self.num_execs = None
        self.host=host

        self.running = False
        self.connected = False

    def connect(self):
        try:
            if self.igt_system.autoConnect():
                self.all_msgs.appendMsg("Connected to IGT System!")
                self.igt_system.enableAmplifier(True)
                self.igt_system.selectOutput(FUS.Output.EXTERNAL)
                self.connected = True
            else:
                self.all_msgs.appendMsg('Could not connect to IGT System. Check if system is plugged in?')
        except Exception as err:
            print('ERROR: ' + str(err))
            io.line_print(traceback.format_exc())
            self.all_msgs.appendMsg('Could not connect to IGT System. Check if system is plugged in?')

    def send_traj(self,seq_data):
        if self.motor is None or not self.motor.connected:
            self.all_msgs.appendMsg('No motor system connected. Movement will be disabled.')
        else:
            self.use_motor = True

        self.trajectory = []
        self.motor_traj = []
        for pulse in seq_data["Sequence"]:
            self.trajectory.append(FUS.Pulse(
                dura = int(pulse["Duration"]*1000.0), #Duration in microseconds
                dela = int(pulse["Delay"]*1000.0), #Delay in microseconds
                ampl = int(pulse["Amplitude"]/100.0 * 1023), #Amplitude in [0,1023]
                freq = int(pulse["Freq"]*1.0e6) #US Frequency in Hz
            ))
            self.motor_traj.append((pulse["MoveX"], pulse["MoveY"], pulse["MoveZ"]))
        self.num_execs = seq_data["ExecutionCount"]
        self.seq_delay = int(seq_data["SequenceDelay"]*1000.0)

        self.num_pulses = self.num_execs * len(self.trajectory)

        #Schedule the FUS Firing
        self.run_thread = multiprocessing.Process(target = self.execute_traj)

        self.all_msgs.appendMsg("Sequence successfully sent.")

    def run(self):
        """Starts the FUS execution queue
        """
        if self.running:
            self.all_msgs.appendMsg("ERROR: Experiment is already running!")
            return
        if not self.connected:
            self.all_msgs.appendMsg("ERROR: Generator is not connected!")
            return

        # Start the execution
        self.run_thread.start()

        self.running = True

    def close(self):
        """Disconnects the IGT System
        """
        if self.connected:
            self.igt_system.enableAmplifier(False)
            self.igt_system.disconnect()
            self.connected = False
            self.all_msgs.appendMsg("Generator shutdown successfully.")
        else:
            self.all_msgs.appendMsg("Generator is already shutdown!")


    def stop(self):
        """Stops the experiment
        """
        if not self.running:
            warnings.warn('<FUS_GEN> Experiment is already stopped')
            return

        self.running = False
        self.igt_system.stopSequence()
        self.run_thread.terminate()
        self.run_thread.join()
        
        self.run_thread = None

        all_msgs.appendMsg('Sequence aborted at ' + io.get_time_string())

    def add_finish(self,start_time):
        """Schedules when to stop the experiment (at the same time as the RPi)

        Parameters
        ----------
        start_time : float
            Number of seconds when to stop the experiment
        """
        self.events.append(threading.Timer(start_time,self.stop))

    def reconnect(self):
        """Reconnects the IGT System
        """
        if self.connected:
            warnings.warn('<FUS_GEN> System is already connected',RuntimeWarning)
            return
        else:
            if self.igt_system.autoConnect():
                print("Connected to IGT System ", self.host)
            else:
                raise EnvironmentError('<FUS_GEN> Could not connect to IGT System')

    def execute_traj(self):
        """Tells the IGT system to execute the current trajectory and then loads the next trajectory if necessary
        into the Generator's buffers

        Parameters
        ----------
        traj_id : int
            Index of the trajectory to be executed
        """
        exec_flags = FUS.ExecFlag.ASYNC_PULSE_RESULT
        self.igt_system.executeSequence(self.num_execs,self.seq_delay,exec_flags)
        for i in range(self.num_pulses):
            if not self.running:
                break                
            measure = self.igt_system.readAsyncPulse()

            #Issue Move command if motor is connected
            if self.motor and self.motor.connected:
                self.motor.moveRel(self.motor_traj[i % len(self.motor_traj)])

            #Print Result of the FUS Shot
            self.all_msgs.appendMsg('FUS RESULT: ' + str(measure))

        self.running = False

        all_msgs.appendMsg('Sequence finished at ' + io.get_time_string())