# -*- test-case-name: epsilon.test.test_release -*-

"""
Automation for most of the release process for Divmod projects.
"""

import sys, re
from os import chdir

from twisted.python.reflect import namedModule
from twisted.python.versions import Version
from twisted.python.usage import Options
from twisted.python.filepath import FilePath
from twisted.python.release import sh, runChdirSafe

from combinator.branchmgr import theBranchManager
from epsilon.structlike import record

class Project(record("name initPath package version")):
    """
    Container for information about a particular Divmod project being released.

    @ivar name: The name of the project.
    @ivar initPath: A C{FilePath} to the Python package of the project.
    @ivar package: A module object, the package for this project.
    @ivar version: The current version of this project.
    """

verstringMatcher = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)$")


def replaceProjectVersion(filename, newversion):
    """
    Write version specification code into the given filename, which
    sets the version to the given version number.

    @param filename: A filename which is most likely a "_version.py"
    under some Twisted project.
    @param newversion: A sequence of three numbers.
    """
    f = open(filename, 'w')
    f.write('''\
# This is an auto-generated file. Use Epsilon/bin/release-divmod to update.
from twisted.python import versions
version = versions.Version(__name__[:__name__.rfind('.')], %s, %s, %s)
''' % tuple(newversion))
    f.close()



def namesToPaths(projectNames, verbose=True):
    """
    Turn names of projects into project objects.

    @type projectNames: C{list} of C{str}
    @param projectNames: The names of Python packages in each project to find
        and for which to create a L{Project} instance.

    @type verbose: C{bool}
    @param verbose: If true, report some information about what happens to
        stdout.

    @rtype: C{list} of L{Project}
    @return: Project instances for each package in C{projectNames}, with
        C{name}, C{initPath}, and C{package} set.
    """
    projectObjects = []
    for projName in projectNames:
        for pfx in '', 'x':
            try:
                projPackage = namedModule(pfx + projName)
            except ImportError:
                pass
            else:
                projPackagePath = FilePath(projPackage.__file__)
                break
        else:
            raise SystemExit("Failed to find Python package for %s."
                             % (projName,))

        realName = projPackagePath.parent().parent().basename()
        projectObjects.append(Project(name=realName,
                                      initPath=projPackagePath,
                                      package=projPackage,
                                      version=None))
        if verbose:
            print 'Found', projName, 'as', realName, 'at', projPackagePath.path
    return projectObjects



def inputNewVersionWithDefault(proj, raw_input=raw_input):
    """
    Ask the user to input a new version number for the given project.  Default
    to the top version in NEWS.txt.

    @type proj: L{Project}
    @param proj: The project for which to get a version.

    @rtype: L{tuple} of C{int}
    @return: A three-tuple giving the new major, minor, and micro version.
    """
    news = proj.initPath.parent().parent().child("NEWS.txt")
    if news.exists():
        f = news.open()
        defaultVersionString = f.read(16).strip().split(' ')[0]
    else:
        defaultVersionString = '0.1.0'
    match = None
    while match is None:
        new_vers = (raw_input("New version for %s (default %s)? "
                             % (proj.name, defaultVersionString)))
        if not new_vers:
            new_vers = defaultVersionString
        match = verstringMatcher.match(new_vers)
        if match is None:
            print 'Invalid format. Use e.g. 2.0.0.'

    major, minor, micro = map(int, match.groups())
    return major, minor, micro



def updateVersionFiles(projectObjects, verbose=True,
                       inputNewVersionWithDefault=inputNewVersionWithDefault,
                       replaceProjectVersion=replaceProjectVersion):
    """
    Gather version information and change _version.py files to contain new
    version number.

    @type projectObjects: C{list} of L{Project} instances
    @param projectObjects: The projects which will have their version
        information updated.

    @type verbose: C{bool}
    @param verbose: If true, report some information about what happens to
        stdout.
    """
    for proj in projectObjects:
        projVersion = inputNewVersionWithDefault(proj)
        if projVersion is None:
            projVersion = proj.package.version
            projVersion = (projVersion.major, projVersion.minor,
                           projVersion.micro)
        projVersionFilePath = proj.initPath.sibling('_version.py')
        replaceProjectVersion(
            projVersionFilePath.path,
            projVersion)
        proj.version = Version(proj.name, *projVersion)
        if verbose:
            print 'Updated version in', projVersionFilePath.path



def doCommit(rootPath, prompt, msg, sh=sh):
    """
    Commit version files and probably NEWS.txt files to version control.

    @type rootPath: L{FilePath}
    @param rootPath: The root path to commit to version control.

    @type prompt: C{bool}
    @param prompt: If true, ask the user before executing any shell commands.

    @type msg: C{str}
    @param msg: Version control commit message.
    """
    cmd = 'svn commit %(rootPath)s -m "%(msg)s"'
    sh(cmd % {'rootPath': rootPath.path, 'msg': msg},
       null=False,
       prompt=prompt)



def doExport(projectName, rootPath, prompt, theBranchManager=theBranchManager, sh=sh):
    """
    Export the repo from SVN into a clean directory.

    @type projectName: C{str}
    @param projectName: The Combinator name of the project to export.

    @type rootPath: L{FilePath}
    @param rootPath: The working copy of the SVN path to export.

    @type prompt: C{bool}
    @param prompt: If true, ask the user before executing any shell commands.

    @rtype: C{tuple} of L{FilePath} and C{str}
    @return: The path to which the export was done and the URI which was
        exported.
    """
    branchRelativePath = theBranchManager.currentBranchFor(projectName)
    branchURI = theBranchManager.projectBranchURI(
        projectName, branchRelativePath)
    exportPath = FilePath('.release').temporarySibling()
    cmd = 'svn export -rHEAD %(rootPath)s %(exportPath)s'
    sh(cmd % {'rootPath': rootPath.path, 'exportPath': exportPath.path},
       null=False,
       prompt=prompt)
    return exportPath, branchURI



def doSourceDist(projectObjects, exportPath, prompt, sh=sh, chdir=chdir):
    """
    Create tarballs with distutils for each project.

    @type projectObjects: C{list} of L{Project} instances
    @param projectObjects: The projects for which to create tarballs.

    @type exportPath: L{FilePath}
    @param exportPath: The directory which contains svn exports of all of the
        projects to operate on.

    @type prompt: C{bool}
    @param prompt: If true, ask the user before executing any shell commands.
    """
    for proj in projectObjects:
        def makeSourceRelease():
            chdir(exportPath.child(proj.name).path)
            cmd = '%(python)s setup.py sdist'
            sh(cmd % {'python': sys.executable},
               null=False,
               prompt=prompt)

        runChdirSafe(makeSourceRelease)



def doSourceUnpack(projectObjects, exportPath, prompt, sh=sh, chdir=chdir):
    """
    Unpack source tarballs for projects.

    @type projectObjects: C{list} of L{Project} instances
    @param projectObjects: The projects for which to unpack tarballs.

    @type exportPath: L{FilePath}
    @param exportPath: The directory which contains svn exports of all of the
        projects to operate on.  These should have previously had tarballs
        created for them with L{doSourceDist}.

    @type prompt: C{bool}
    @param prompt: If true, ask the user before executing any shell commands.
    """
    for proj in projectObjects:
        def unpackSourceRelease():
            projectExport = exportPath.child(proj.name)
            chdir(projectExport.child('dist').path)
            cmd = 'tar xzf %(projectName)s-%(projectVersion)s.tar.gz'
            sh(cmd % {'projectName': proj.name,
                      'projectVersion': proj.version.short()},
               null=False,
               prompt=prompt)

        runChdirSafe(unpackSourceRelease)



def doInstall(projectObjects, exportPath, prompt, sh=sh, chdir=chdir):
    """
    Run distutils installation for each project.

    @type projectObjects: C{list} of L{Project} instances
    @param projectObjects: The projects to install.

    @type exportPath: L{FilePath}
    @param exportPath: The directory which contains svn exports of all of the
        projects to operate on.  These should have previously had tarballs
        created and unpacked with L{doSourceDist} and L{doSourceUnpack}.

    @type prompt: C{bool}
    @param prompt: If true, ask the user before executing any shell commands.

    @rtype: L{FilePath}
    @return: The installation prefix path.
    """
    installPath = FilePath('.install').temporarySibling()
    for proj in projectObjects:
        def installSourceRelease():
            projectExport = exportPath.child(proj.name)
            projectDir = '%s-%s' % (proj.name, proj.version.short())
            unpackPath = projectExport.child('dist').child(projectDir)
            chdir(unpackPath.path)
            cmd = '%(python)s setup.py install --prefix %(installPath)s'
            sh(cmd % {'python': sys.executable,
                      'installPath': installPath.path},
               null=False,
               prompt=prompt)

        runChdirSafe(installSourceRelease)
    return installPath



def runTests(projectObjects, installPath, prompt, sh=sh):
    """
    Run unit tests for each project.

    @type projectObjects: C{list} of L{Project} instances
    @param projectObjects: The projects for which to run tests.

    @type installPath: L{FilePath}
    @param installPath: The installation prefix path which contains the
        packages for which to run tests.

    @type prompt: C{bool}
    @param prompt: If true, ask the user before executing any shell commands.
    """
    # distutils.sysconfig.get_python_lib(prefix=...) might be more appropriate
    libPath = installPath.child('lib')
    pythonPath = libPath.child('python%d.%d' % sys.version_info[:2])
    siteInstallPath = pythonPath.child('site-packages')
    for proj in projectObjects:
        def testSourceInstall():
            cmd = 'PYTHONPATH=%(installPath)s:$PYTHONPATH trial %(projectName)s'
            sh(cmd % {'installPath': siteInstallPath.path,
                      'projectName': proj.initPath.parent().basename()},
               null=False,
               prompt=prompt)

        runChdirSafe(testSourceInstall)



def makeTags(projectObjects, repo, branchURI, prompt, sh=sh):
    """
    Make SVN tags for the code in these projects.

    @type projectObjects: C{list} of L{Project} instances
    @param projectObjects: The projects for which to make tags.

    @type repo: C{str}
    @param repo: The segment of the repository URI immediately before the
        {trunk,branches,tags} segment.

    @type branchURI: C{str}
    @param branchURI: The URI of the branch for which to create a tag.

    @type prompt: C{bool}
    @param prompt: If true, ask the user before executing any shell commands.
    """
    #XXX Maybe this should be a parameter too?
    tagRootURI = 'svn+ssh://divmod.org/svn/%s/tags/releases' % (repo,)
    for proj in projectObjects:
        def tagRelease():
            source = '%(branchURI)s/%(projectName)s'
            dest = '%(tagRootURI)s/%(projectName)s-%(projectVersion)s'
            cmd = 'svn cp %s %s -m "Tagging release"' % (source, dest)
            sh(cmd % {'branchURI': branchURI,
                      'projectName': proj.name,
                      'tagRootURI': tagRootURI,
                      'projectVersion': proj.version.short()},
               null=False,
               prompt=prompt)

        runChdirSafe(tagRelease)



def collectTarballs(projectObjects, exportPath, releasePath):
    """
    Collect tarballs in the releases/ directory.

    @type projectObjects: C{list} of L{Project} instances
    @param projectObjects: The projects for which to make tags.

    @type exportPath: L{FilePath}
    @param exportPath: The directory which contains release tarballs previously
        generated with L{doSourceDist}.

    @type releasePath: L{FilePath}
    @param releasePath: A directory which will have a I{releases} subdirectory
        added to it (if one does not already exist) into which the tarballs
        will be moved.
    """
    releasePath = releasePath.child('releases')
    if not releasePath.isdir():
        releasePath.makedirs()

    for proj in projectObjects:
        def collectTarball():
            projectExport = exportPath.child(proj.name)
            releaseFile = '%s-%s.tar.gz' % (proj.name,
                                            proj.version.short())
            projectPath = projectExport.child('dist').child(releaseFile)
            projectPath.moveTo(releasePath.child(releaseFile))
        runChdirSafe(collectTarball)



def release(rootPath, repo, projectNames, prompt):
    """
    Prompt for new versions of the indicated projects and re-write their
    version information.

    @type rootPath: L{FilePath}
    @param rootPath: The root of the working copy from which to release.

    @param projectNames: A C{list} of C{str} which name Python modules for
    projects in the Divmod repository.
    """
    if not projectNames:
        raise SystemExit("Specify some package names to release.")

    projectObjects = namesToPaths(projectNames)
    updateVersionFiles(projectObjects)

    doCommit(rootPath, prompt, "Version updates for release")
    exportPath, branchURI = doExport(repo, rootPath, prompt)

    doSourceDist(projectObjects, exportPath, prompt)
    doSourceUnpack(projectObjects, exportPath, prompt)
    installPath = doInstall(projectObjects, exportPath, prompt)

    runTests(projectObjects, installPath, prompt)
    makeTags(projectObjects, repo, branchURI, prompt)
    collectTarballs(projectObjects, exportPath, FilePath('.'))



class ReleaseOptions(Options):
    optParameters = [['project', 'P', 'Divmod',
                      'The Combinator-managed project name in which to find '
                      'the packages being released.']]

    def parseArgs(self, *packages):
        self['packageNames'] = packages



def main():
    """
    Parse options from C{sys.argv} and perform a release based on them.

    The working directory of the process in which this is called should be the
    base of a working copy of the release branch which is being used to
    generate the release.

    Version files for packages being released will be updated and committed, a
    tag will be created, release tarballs will be generated using distutils,
    and the results will be unpacked, installed, and have their unit tests run
    using trial.
    """
    o = ReleaseOptions()
    o.parseOptions(sys.argv[1:])
    release(FilePath('.'), o['project'], o['packageNames'], True)
