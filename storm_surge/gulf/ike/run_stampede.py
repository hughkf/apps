#!/usr/bin/env python

r"""Script for running OpenMP MIC tests on Stampede"""

import batch.stampede

class StampedeStormJob(batch.stampede.StampedeJob):

    def __init__(self, omp_num_threads, mic_omp_num_threads):

        super(StampedeStormJob, self).__init__()

        self.omp_num_threads = omp_num_threads
        self.mic_omp_num_threads = mic_omp_num_threads

        self.type = "surge"
        self.name = "omp-test"
        self.prefix = "h%sm%s" % (self.omp_num_threads, self.mic_omp_num_threads)
        self.executable = "xgeoclaw"

        if self.mic_omp_num_threads == 0:
            self.queue = "serial"
        else:
            self.queue = "normal-mic"

        # Create base data object
        import setrun
        self.rundata = setrun.setrun()

if __name__ == "__main__":

    # mic_threads = [0,122]
    host_threads = [1, 2, 4, 8, 12, 16]
    mic_threads = [0]

    jobs = []
    for host_thread_count in host_threads:
        for mic_thread_count in mic_threads:
            jobs.append(StampedeStormJob(host_thread_count, mic_thread_count))

    controller = batch.stampede.StampedeBatchController(jobs)
    controller.run()