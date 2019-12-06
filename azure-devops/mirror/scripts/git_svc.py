""" git_svc.py

Module that manage git actions
"""

import git
import pathlib
import typing


class GitSVC(object):
    __repo: git.Repo
    """
    private repo variable
    """
    REMOTE_ORIGIN: str = "origin"
    """
    name of the origin remote
    """
    REMOTE_UPSTREAM: str = "upstream"
    """
    name of the upstream remote
    """

    def __init__(self, git_uri: str, local_path: str) -> None:
        __repo = git.Repo.clone_from(url=git_uri, to_path=local_path)
        # make sure repo is cloned
        assert pathlib.Path.exists(pathlib.Path(local_path))
        # make sure repo is not empty
        assert not __repo.bare
        # make sure repo is clean
        assert not __repo.is_dirty()
        self.__repo = __repo

    def remote_add_upstream(self, upstream_uri: str) -> None:
        """
        add a uri to the upstream remote
        """
        assert self.REMOTE_UPSTREAM not in self.__repo.remotes
        self.__repo.create_remote(self.REMOTE_UPSTREAM, upstream_uri)
        assert self.__repo.remote(self.REMOTE_UPSTREAM).exists()

    def fetch(self, remotes: typing.List[str]) -> None:
        """
        fetch update from a list of remotes
        """
        for remote in remotes:
            assert self.__repo.remote(remote).exists()
            self.__repo.remote(remote).fetch()

    def checkout_remote_branch(
        self, local_branch, remote: str, remote_branch: str
    ) -> str:
        """
        check out a remote branch
        local_branch: the new local branch that will be created
        remote: one of the git remotes
        remote_branch: the branch name of the git remote
        """
        assert self.__repo.remote(remote).exists()
        r = self.__repo.remote(remote)
        if local_branch not in self.__repo.heads:
            self.__repo.create_head(local_branch, r.refs[remote_branch])
        self.__repo.heads[local_branch].checkout()
        sha1 = self.__repo.head.object.hexsha[:8]
        assert sha1 != ""
        return sha1

    def merge(
        self, base: str, feature: str, message: str, force_commit: bool = False
    ) -> bool:
        """
        merge two branches
        force_commit: when it is set to True, commit the merge with merge conflict
        """
        assert base in self.__repo.branches
        assert feature in self.__repo.branches
        self.__repo.heads[base].checkout()
        try:
            self.__repo.git.merge(feature, "-m", message)
            return True
        except git.exc.GitCommandError:
            if not force_commit:
                raise
            print("git_svc merge: git auto merge failed, force commit the changes")
            self.__repo.git.add(".")
            self.__repo.git.commit("-m", message)
            return False

    def push(self, upstream: str, local_branch: str, upstream_branch: str) -> None:
        """
        push local branch to upstream
        """
        branch = f"{local_branch}:{upstream_branch}"
        assert self.__repo.remote(upstream).exists()
        assert local_branch in self.__repo.heads
        self.__repo.git.push(upstream, branch, "-f")
        self.__repo.git.push(upstream, "--tags")

    def remote_remove_upstream(self) -> None:
        """
        remote the upstream remote from the local repo
        """
        assert self.__repo.remote(self.REMOTE_UPSTREAM).exists()
        self.__repo.delete_remote(self.REMOTE_UPSTREAM)
        assert self.REMOTE_UPSTREAM not in self.__repo.remotes
