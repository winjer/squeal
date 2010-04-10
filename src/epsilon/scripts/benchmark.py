# -*- test-case-name: epsilon.test.test_benchmark -*-

"""
Functions for running a Python file in a child process and recording resource
usage information and other statistics about it.
"""

import os, time, sys, socket, StringIO, pprint, errno

import twisted
from twisted.python import log, filepath, failure, util
from twisted.internet import reactor, protocol, error, defer
from twisted.protocols import policies

import epsilon
from epsilon import structlike

from epsilon import juice
from epsilon.test import utils


class diskstat(structlike.record(
    'readCount mergedReadCount readSectorCount readMilliseconds '
    'writeCount mergedWriteCount writeSectorCount writeMilliseconds '
    'outstandingIOCount ioMilliseconds weightedIOMilliseconds')):
    """
    Represent the I/O stats of a single device, as reported by Linux's disk
    stats.
    """



class partitionstat(structlike.record(
    'readCount readSectorCount writeCount writeSectorCount')):
    """
    Like diskstat, but for a partition.  Less information is made available by
    Linux for partitions, so this has fewer attributes.
    """



def parseDiskStatLine(L):
    """
    Parse a single line from C{/proc/diskstats} into a two-tuple of the name of
    the device to which it corresponds (ie 'hda') and an instance of the
    appropriate record type (either L{partitionstat} or L{diskstat}).
    """
    parts = L.split()
    device = parts[2]
    if len(parts) == 7:
        factory = partitionstat
    else:
        factory = diskstat
    return device, factory(*map(int, parts[3:]))



def parseDiskStats(fObj):
    """
    Parse a file-like object containing lines formatted like those in
    C{/proc/diskstats}.  Yield two-tuples of information for each line.
    """
    for L in fObj:
        yield parseDiskStatLine(L)



def captureStats():
    """
    Parse the current contents of C{/proc/diskstats} into a dict mapping device
    names to instances of the appropriate stat record.
    """
    return dict(parseDiskStats(file('/proc/diskstats')))



class ResourceSnapshot(structlike.record('time disk partition size')):
    """
    Represents the state of some resources on the system at a particular moment
    in time.

    @ivar time: The time at which the stats associated with this instance were
    recorded.

    @ivar disk: A C{diskstat} instance created from stats available that the
    given time.

    @ivar partition: A C{diskstat} instance created from stats available that
    the given time.

    @ivar size: Total size of all files beneath a particular directory.
    """



class ProcessDied(Exception):
    """
    Encapsulates process state and failure mode.
    """
    def __init__(self, exitCode, signal, status, output):
        self.exitCode = exitCode
        self.signal = signal
        self.status = status
        self.output = output
        Exception.__init__(self)



class BasicProcess(protocol.ProcessProtocol, policies.TimeoutMixin):
    """
    The simplest possible process protocol.  It doesn't do anything except what
    is absolutely mandatory of any conceivable ProcessProtocol.
    """
    timedOut = False

    BACKCHANNEL_OUT = 3
    BACKCHANNEL_IN = 4

    def __init__(self, whenFinished, path):
        self.whenFinished = whenFinished
        self.path = path
        self.output = []


    def connectionMade(self):
        self.setTimeout(900.0)


    def timeoutConnection(self):
        self.timedOut = True
        self.transport.signalProcess('KILL')


    def childDataReceived(self, childFD, data):
        self.resetTimeout()
        self.output.append((childFD, data))


    def childConnectionLost(self, childFD):
        self.resetTimeout()
        self.output.append((childFD, None))


    def processEnded(self, reason):
        # XXX Okay, I'm a liar.  This doesn't do everything.  Strictly speaking
        # we shouldn't fire completion notification until the process has
        # terminated *and* the file descriptors have all been closed.  We're
        # not supporting passing file descriptors from the child to a
        # grandchild here, though.  Don't Do It.
        d, self.whenFinished = self.whenFinished, None
        o, self.output = self.output, None
        if reason.check(error.ProcessDone):
            d.callback((self, reason.value.status, o))
        elif self.timedOut:
            d.errback(error.TimeoutError())
        elif reason.check(error.ProcessTerminated):
            d.errback(failure.Failure(ProcessDied(
                reason.value.exitCode,
                reason.value.signal,
                reason.value.status, o)))
        else:
            d.errback(reason.value)
        self.setTimeout(None)


    def spawn(cls, executable, args, path, env, spawnProcess=None):
        """
        Run an executable with some arguments in the given working directory with
        the given environment variables.

        Returns a Deferred which fires with a two-tuple of (exit status, output
        list) if the process terminates without timing out or being killed by a
        signal.  Otherwise, the Deferred errbacks with either L{error.TimeoutError}
        if any 10 minute period passes with no events or L{ProcessDied} if it is
        killed by a signal.

        On success, the output list is of two-tuples of (file descriptor, bytes).
        """
        d = defer.Deferred()
        proto = cls(d, filepath.FilePath(path))
        if spawnProcess is None:
            spawnProcess = reactor.spawnProcess
        spawnProcess(
            proto,
            executable,
            [executable] + args,
            path=path,
            env=env,
            childFDs={0: 'w', 1: 'r', 2: 'r',
                      cls.BACKCHANNEL_OUT: 'r',
                      cls.BACKCHANNEL_IN: 'w'})
        return d
    spawn = classmethod(spawn)



class Change(object):
    """
    Stores two ResourceSnapshots taken at two different times.
    """
    def start(self, path, disk, partition):
        # Do these three things as explicit, separate statments to make sure
        # gathering disk stats isn't accidentally included in the duration.
        startSize = getSize(path)
        beforeDiskStats = captureStats()
        startTime = time.time()
        self.before = ResourceSnapshot(
            time=startTime,
            disk=beforeDiskStats.get(disk, None),
            partition=beforeDiskStats.get(partition, None),
            size=startSize)


    def stop(self, path, disk, partition):
        # Do these three things as explicit, separate statments to make sure
        # gathering disk stats isn't accidentally included in the duration.
        endTime = time.time()
        afterDiskStats = captureStats()
        endSize = getSize(path)
        self.after = ResourceSnapshot(
            time=endTime,
            disk=afterDiskStats.get(disk, None),
            partition=afterDiskStats.get(partition, None),
            size=endSize)



class BenchmarkProcess(BasicProcess):

    START = '\0'
    STOP = '\1'


    def __init__(self, *a, **kw):
        BasicProcess.__init__(self, *a, **kw)

        # Figure out where the process is running.
        self.partition = discoverCurrentWorkingDevice().split('/')[-1]
        self.disk = self.partition.rstrip('0123456789')

        # Keep track of stats for the entire process run.
        self.overallChange = Change()
        self.overallChange.start(self.path, self.disk, self.partition)

        # Just keep track of stats between START and STOP events.
        self.benchmarkChange = Change()


    def connectionMade(self):
        return BasicProcess.connectionMade(self)


    def startTiming(self):
        self.benchmarkChange.start(self.path, self.disk, self.partition)
        self.transport.writeToChild(self.BACKCHANNEL_IN, self.START)


    def stopTiming(self):
        self.benchmarkChange.stop(self.path, self.disk, self.partition)
        self.transport.writeToChild(self.BACKCHANNEL_IN, self.STOP)


    def childDataReceived(self, childFD, data):
        if childFD == self.BACKCHANNEL_OUT:
            self.resetTimeout()
            for byte in data:
                if byte == self.START:
                    self.startTiming()
                elif byte == self.STOP:
                    self.stopTiming()
                else:
                    self.transport.signalProcess('QUIT')
        else:
            return BasicProcess.childDataReceived(self, childFD, data)


    def processEnded(self, reason):
        self.overallChange.stop(self.path, self.disk, self.partition)
        return BasicProcess.processEnded(self, reason)



STATS_VERSION = 0
class Results(juice.Command):
    commandName = 'Result'
    arguments = [
        # Stats version - change this whenever the meaning of something changes
        # or a field is added or removed.
        ('version', juice.Integer()),

        # If an error occurred while collecting these stats - this probably
        # means they're bogus.
        ('error', juice.Boolean()),

        # If a particular timeout (See BasicProcess.connectionMade) elapsed
        # with no events whatsoever from the benchmark process.
        ('timeout', juice.Boolean()),

        # A unique name identifying the benchmark for which these are stats.
        ('name', juice.Unicode()),

        # The name of the benchmark associated with these stats.
        ('host', juice.Unicode()),

        # The sector size of the disk on which these stats were collected
        # (sectors are a gross lie, this is really the block size, and
        # everything else that talks about sectors is really talking about
        # blocks).
        ('sector_size', juice.Integer()),

        # Hex version info for the Python which generated these stats.
        ('python_version', juice.Unicode()),

        # Twisted SVN revision number used to generate these stats.
        ('twisted_version', juice.Unicode()),

        # Divmod SVN revision number used to generate these stats.
        ('divmod_version', juice.Unicode()),

        # Number of seconds between process startup and termination.
        ('elapsed', juice.Float()),

        # Size, in bytes, of the directory in which the child process was run.
        ('filesystem_growth', juice.Integer()),

        # Number of reads issued on the partition over the lifetime of the
        # child process.  This may include reads from other processes, if any
        # were active on the same disk when the stats were collected.
        ('read_count', juice.Integer(optional=True)),

        # Number of sectors which were read from the partition over the
        # lifetime of the child process. Same caveat as above.
        ('read_sectors', juice.Integer(optional=True)),

        # Number of writes issued to the partition over the lifetime of the
        # child process.  Same caveat as above.
        ('write_count', juice.Integer(optional=True)),

        # Number of sectors which were written to the partition over the
        # lifetime of the child process.  Same caveat as above.
        ('write_sectors', juice.Integer(optional=True)),

        # Number of milliseconds spent blocked on reading from the disk over
        # the lifetime of the child process.  Same caveat as above.
        ('read_ms', juice.Integer(optional=True)),

        # Number of milliseconds spent blocked on writing to the disk over the
        # lifetime of the child process.  Same caveat as above.
        ('write_ms', juice.Integer(optional=True)),
        ]


hostname = socket.gethostname()
assert hostname != 'localhost', "Fix your computro."

def formatResults(name, sectorSize, before, after, error, timeout):
    output = StringIO.StringIO()
    jj = juice.Juice(issueGreeting=False)
    tt = utils.FileWrapper(output)
    jj.makeConnection(tt)

    if after.partition is not None:
        read_count = after.partition.readCount - before.partition.readCount
        read_sectors = after.partition.readSectorCount - before.partition.readSectorCount
        write_count = after.partition.writeCount - before.partition.writeCount
        write_sectors = after.partition.writeSectorCount - before.partition.writeSectorCount
    else:
        read_count = None
        read_sectors = None
        write_count = None
        write_sectors = None

    if after.disk is not None:
        read_ms = after.disk.readMilliseconds - before.disk.readMilliseconds
        write_ms = after.disk.writeMilliseconds - before.disk.writeMilliseconds
    else:
        read_ms = None
        write_ms = None

    twisted_version = twisted.version._getSVNVersion()
    if twisted_version is None:
        twisted_version = twisted.version.short()
    epsilon_version = epsilon.version._getSVNVersion()
    if epsilon_version is None:
        epsilon_version = epsilon.version.short()

    Results(
        version=STATS_VERSION,
        error=error,
        timeout=timeout,
        name=name,
        host=hostname,
        elapsed=after.time - before.time,
        sector_size=sectorSize,
        read_count=read_count,
        read_sectors=read_sectors,
        read_ms=read_ms,
        write_count=write_count,
        write_sectors=write_sectors,
        write_ms=write_ms,
        filesystem_growth=after.size - before.size,
        python_version=unicode(sys.hexversion),
        twisted_version=twisted_version,
        divmod_version=epsilon_version,
        ).do(jj, requiresAnswer=False)
    return output.getvalue()



def reportResults(results):
    print results
    print
    fObj = file('output', 'ab')
    fObj.write(results)
    fObj.close()



def discoverCurrentWorkingDevice():
    """
    Return a short string naming the device which backs the current working
    directory, ie C{/dev/hda1}.
    """
    possibilities = []
    cwd = os.getcwd()
    for L in file('/etc/mtab'):
        parts = L.split()
        if cwd.startswith(parts[1]):
            possibilities.append((len(parts[1]), parts[0]))
    possibilities.sort()
    return possibilities[-1][-1]



def getSize(p):
    """
    @type p: L{twisted.python.filepath.FilePath}
    @return: The size, in bytes, of the given path and all its children.
    """
    return sum(getOneSize(ch) for ch in p.walk())


def getOneSize(ch):
    """
    @type ch: L{twisted.python.filepath.FilePath}
    @return: The size, in bytes, of the given path only.
    """
    try:
        return ch.getsize()
    except OSError, e:
        if e.errno == errno.ENOENT:
            # XXX FilePath is broken
            if os.path.islink(ch.path):
                return len(os.readlink(ch.path))
            else:
                raise
        else:
            raise



def getSectorSize(p):
    return os.statvfs(p.path).f_bsize


def _bench(name, workingPath, function):
    d = function()
    def later(result):
        err = timeout = False
        if isinstance(result, failure.Failure):
            err = True
            if result.check(error.TimeoutError):
                log.msg("Failing because timeout!")
                timeout = True
            elif result.check(ProcessDied):
                log.msg("Failing because Failure!")
                pprint.pprint(result.value.output)
                print result.value.exitCode, result.value.signal
            else:
                log.err(result)
        else:
            proto, status, output = result
            stderr = [bytes for (fd, bytes) in output if fd == 2]
            if status or stderr != [None]:
                err = True
                log.msg("Failing because stderr or bad status")
                pprint.pprint(result)

            for n, change in [(name + '-overall', proto.overallChange),
                              (name + '-benchmark', proto.benchmarkChange)]:
                reportResults(formatResults(
                    n,
                    getSectorSize(workingPath),
                    change.before,
                    change.after,
                    err,
                    timeout))

    return d.addBoth(later)



def bench(name, path, func):
    log.startLogging(sys.stdout)
    log.msg("Running " + name)

    d = _bench(name, path, func)
    d.addErrback(log.err)
    d.addCallback(lambda ign: reactor.stop())

    reactor.run()


def makeBenchmarkRunner(path, args):
    """
    Make a function that will run two Python processes serially: first one
    which calls the setup function from the given file, then one which calls
    the execute function from the given file.
    """
    def runner():
        return BenchmarkProcess.spawn(
            executable=sys.executable,
            args=['-Wignore'] + args,
            path=path.path,
            env=os.environ)
    return runner



def start():
    """
    Start recording stats.  Call this from a benchmark script when your setup
    is done.  Call this at most once.

    @raise RuntimeError: Raised if the parent process responds with anything
    other than an acknowledgement of this message.
    """
    os.write(BenchmarkProcess.BACKCHANNEL_OUT, BenchmarkProcess.START)
    response = util.untilConcludes(os.read, BenchmarkProcess.BACKCHANNEL_IN, 1)
    if response != BenchmarkProcess.START:
        raise RuntimeError(
            "Parent process responded with %r instead of START " % (response,))



def stop():
    """
    Stop recording stats.  Call this from a benchmark script when the code you
    want benchmarked has finished.  Call this exactly the same number of times
    you call L{start} and only after calling it.

    @raise RuntimeError: Raised if the parent process responds with anything
    other than an acknowledgement of this message.
    """
    os.write(BenchmarkProcess.BACKCHANNEL_OUT, BenchmarkProcess.STOP)
    response = util.untilConcludes(os.read, BenchmarkProcess.BACKCHANNEL_IN, 1)
    if response != BenchmarkProcess.STOP:
        raise RuntimeError(
            "Parent process responded with %r instead of STOP" % (response,))



def main():
    """
    Run me with the filename of a benchmark script as an argument.  I will time
    it and append the results to a file named output in the current working
    directory.
    """
    name = sys.argv[1]
    path = filepath.FilePath('.stat').temporarySibling()
    path.makedirs()
    func = makeBenchmarkRunner(path, sys.argv[1:])
    try:
        bench(name, path, func)
    finally:
        path.remove()



if __name__ == '__main__':
    main()
