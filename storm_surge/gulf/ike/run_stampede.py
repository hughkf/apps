#!/usr/bin/env python

r"""Script for running OpenMP MIC tests on Stampede"""

import batch.stampede

class StampedeStormJob(batch.stampede.StampedeJob):

    def __init__(self, omp_num_threads, mic_omp_num_threads, mic_affinity="balanced"):

        super(StampedeStormJob, self).__init__()

        self.omp_num_threads = omp_num_threads
        self.mic_omp_num_threads = mic_omp_num_threads
        # Affinity on MIC, options are none, compact, explicit, scatter, balanced 
        self.mic_affinity = mic_affinity
        self.maxgrid1d = 60

        self.type = "surge"
        self.name = "omp-test"
        self.prefix = "h%sm%sa%sg%s" % (self.omp_num_threads, self.mic_omp_num_threads, 
                                        self.mic_affinity[0], self.maxgrid1d)
        self.executable = "xgeoclaw"

        if self.mic_omp_num_threads == 0:
            self.queue = "serial"
        else:
            self.queue = "normal-mic"

        # Create base data object
        import setrun
        self.rundata = setrun.setrun()

if __name__ == "__main__":

    host_threads = [4, 8, 12, 16]
    #mic_threads = [240 / thread_count for thread_count in host_threads]
    mic_threads = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]

    jobs = []
    for host_thread_count in host_threads:
        for mic_thread_count in mic_threads:
            jobs.append(StampedeStormJob(host_thread_count, mic_thread_count))

    controller = batch.stampede.StampedeBatchController(jobs)
    controller.run()
