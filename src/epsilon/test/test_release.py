"""
Tests for Divmod package-release automation.
"""
from sys import executable, version_info

from twisted.trial.unittest import TestCase
from twisted.python.versions import Version
from twisted.python.filepath import FilePath

import epsilon

from epsilon.release import (
    namesToPaths, inputNewVersionWithDefault, updateVersionFiles, doCommit,
    doExport, doSourceDist, doSourceUnpack, doInstall, runTests, makeTags,
    collectTarballs, replaceProjectVersion, Project)


class ReleaseTests(TestCase):
    """
    Tests for Divmod package-release automation.
    """
    def setUp(self):
        self.currentDirectory = None
        self.commands = []

    def test_replaceProjectVersion(self):
        """
        Test that replaceProjectVersion generates a _version.py correctly.
        """
        f = self.mktemp()
        replaceProjectVersion(f, (7,8,9))
        self.assertEqual(open(f).read(), """\
# This is an auto-generated file. Use Epsilon/bin/release-divmod to update.
from twisted.python import versions
version = versions.Version(__name__[:__name__.rfind('.')], 7, 8, 9)
""")

    def test_namesToPaths(self):
        """
        Test that package names get resolved to the correct paths.
        """
        project = namesToPaths(["epsilon"], False)[0]
        self.assertEqual(project.name, "Epsilon")
        self.assertEqual(project.initPath.path, epsilon.__file__)
        self.assertEqual(project.package, epsilon)


    def test_inputNewVersionWithDefault(self):
        """
        L{inputNewVersionWithDefault} should prompt for a new version number,
        using C{raw_input}, finding the current version number in a I{NEWS.txt}
        file in the grandparent of the C{initPath} of the project it is passed
        and supplying that as a default.
        """
        projectPath = FilePath(self.mktemp()).child('FakeProject')
        projectPath.makedirs()
        projectPath.child('NEWS.txt').setContent('0.9.99')

        packagePath = projectPath.child('fakeproject')
        initPath = packagePath.child('__init__.py')
        project = Project(name="FakeProject", initPath=initPath,
                          package=None, version=None)

        def checkPrompt(prompt):
            self.assertEqual(prompt, "New version for FakeProject (default 0.9.99)? ")
            return ""

        self.assertEqual(
            inputNewVersionWithDefault(project, raw_input=checkPrompt),
            (0, 9, 99))
        self.assertEqual(
            inputNewVersionWithDefault(project, raw_input=lambda _: "6.7.89"),
            (6, 7, 89))


    def test_updateVersionFiles(self):
        """
        C{updateVersionFiles} should rewrite I{_version.py} for the packages of
        the projects it is passed so that they include new version information,
        as provided by repeated calls to L{inputNewVersionWithDefault}.
        """
        initPath = FilePath(self.mktemp())
        project = Project(name="Epsilon", initPath=initPath,
                          package=None, version=None)
        def checkReplaceVersion(path, version):
            self.assertEqual(path, initPath.sibling("_version.py").path)

        updateVersionFiles(
            [project], False,
            inputNewVersionWithDefault=lambda _: (4, 5, 6),
            replaceProjectVersion=checkReplaceVersion)

        self.assertEqual(project.version.package, "Epsilon")
        self.assertEqual(project.version.major, 4)
        self.assertEqual(project.version.minor, 5)
        self.assertEqual(project.version.micro, 6)


    def test_doCommit(self):
        """
        C{doCommit} should execute a shell command which does an svn commit on
        the given path with the given commit message.
        """
        commands = []
        def fakeShell(cmd, null, prompt):
            commands.append((cmd, null, prompt))
        def checkSVNCommand(cmd, null, prompt):
            self.assertEqual(cmd,
                             'svn commit /test/path -m "a great commit"')
        doCommit(FilePath("/test/path"),
                 False, "a great commit",
                 sh=fakeShell)
        self.assertEqual(
            commands,
            [('svn commit /test/path -m "a great commit"', False, False)])


    def test_doExport(self):
        """
        C{doExport} should execute a shell command which does an svn export of
        the current branch of the indicated project to the given path.
        """
        currentLookups = []
        branchLookups = []
        class FakeBranchManager:
            def currentBranchFor(self, repo):
                currentLookups.append(repo)
                return "branch-1"

            def projectBranchURI(self, repo, relpath):
                branchLookups.append((repo, relpath))
                return "http://branch/uri/"

        commands = []
        def fakeShell(cmd, null, prompt):
            commands.append((cmd, null, prompt))

        exportPath, branchURI = doExport(
            'Divmod', FilePath("/test/path"), False,
            theBranchManager=FakeBranchManager(),
            sh=fakeShell)
        self.assertEqual(currentLookups, ["Divmod"])
        self.assertEqual(branchLookups, [("Divmod", "branch-1")])
        self.assertEqual(branchURI, "http://branch/uri/")
        self.assertEqual(
            commands,
            [('svn export -rHEAD /test/path ' + exportPath.path,
              False, False)])


    def fakeChdir(self, path):
        # This is a very dumb implementation of chdir
        if path.startswith('/'):
            self.currentDirectory = path
        else:
            raise NotImplementedError("Sorry - path logic too difficult.")


    def fakeShell(self, command, null, prompt):
        self.commands.append((self.currentDirectory, command, null, prompt))


    def test_doSourceDist(self):
        """
        C{doSourceDist} should execute a shell command which runs the I{sdist}
        subcommand of the I{setup.py} for each project given.
        """
        project = Project(name="Foo", initPath=FilePath(self.mktemp()),
                          package=None, version=None)
        doSourceDist(
            [project], FilePath("/test/path"), False,
            sh=self.fakeShell, chdir=self.fakeChdir)

        self.assertEqual(
            self.commands,
            [("/test/path/Foo",
              executable + " setup.py sdist", False, False)])


    def test_doSourceUnpack(self):
        """
        C{doSourceUnpack} should execute a shell command which runs an untar
        command on the release tarball for the given projects.  It should run
        each command in the dist directory of the corresponding project.
        """
        project = Project(name="Foo", initPath=FilePath(self.mktemp()),
                          version=Version("Foo", 1, 2, 3), package=None)

        doSourceUnpack(
            [project], FilePath("/test/path"), False,
            sh=self.fakeShell, chdir=self.fakeChdir)

        self.assertEqual(
            self.commands,
            [("/test/path/Foo/dist",
              "tar xzf Foo-1.2.3.tar.gz", False, False)])


    def test_doInstall(self):
        """
        C{doInstall} should execute a shell command which runs the I{install}
        subcommand of the I{setup.py} for each project given.  It should run
        each command in the unpacked source directory of each project.
        """
        project = Project(name="Foo", initPath=FilePath(self.mktemp()),
                          version=Version("Foo", 1, 2, 3), package=None)

        installedPath = doInstall(
            [project], FilePath("/test/path"), False,
            sh=self.fakeShell, chdir=self.fakeChdir)

        self.assertEqual(
            self.commands,
            [("/test/path/Foo/dist/Foo-1.2.3",
              executable + " setup.py install --prefix " + installedPath.path,
              False, False)])


    def test_runTests(self):
        """
        C{runTests} should execute a shell command which runs the unit tests
        for all of the given projects.
        """
        prefix = "/test/path/lib/python%d.%d/site-packages" % version_info[:2]
        initPath = FilePath(prefix).child("foo").child("__init__.py")
        runTests(
            [Project(name="Foo", initPath=initPath,
                     package=None, version=None)],
            FilePath("/test/path"), False,
            sh=self.fakeShell)

        path = [prefix, '$PYTHONPATH']
        self.assertEqual(
            self.commands,
            [(None,
              "PYTHONPATH=" + ":".join(path) + " trial foo",
              False, False)])


    def test_makeTags(self):
        """
        C{makeTags} should execute a shell command which creates a release tag
        of the given release branch for each given project.
        """
        project = Project(name="Foo", initPath=self.mktemp(),
                          version=Version("Foo", 1, 2, 3), package=None)
        makeTags(
            [project], "Stuff",
            "svn+ssh://divmod.org/svn/Stuff/branches/release-1",
            False,
            sh=self.fakeShell)

        self.assertEqual(
            self.commands,
            [(None,
              "svn cp svn+ssh://divmod.org/svn/Stuff/branches/release-1/Foo "
              "svn+ssh://divmod.org/svn/Stuff/tags/releases/Foo-1.2.3 "
              '-m "Tagging release"', False, False)])


    def test_collectTarballs(self):
        """
        C{collectTarballs} should move the release tarball for each given
        project into a directory named I{releases} of the current working
        directory.
        """
        moves = []
        class FakeFilePath(FilePath):
            def moveTo(self, target):
                moves.append((self, target))
        FakeFilePath.clonePath = FakeFilePath
        project = Project(name="Foo", initPath=FakeFilePath(self.mktemp()),
                          version=Version("Foo", 1, 2, 3), package=None)
        releasePath = FilePath(self.mktemp())
        collectTarballs([project], FakeFilePath("/test/path"), releasePath)
        self.assertEqual(
            moves,
            [(FilePath('/test/path/Foo/dist/Foo-1.2.3.tar.gz'),
              releasePath.child('releases').child('Foo-1.2.3.tar.gz'))])


