""" main.py

Module that will mirror another github repo.

Will merge changes from an upstream repo and branch into a target repo and branch. Will create a PR with that merged result, and run any CI on that change. 

Usage:
  main.py --source_git_uri=URI --source_branch=BR --upstream_git_uri=URI --upstream_branch=BR --pat=PAT --organization_url=URL --project_id=PROJ --repository=NM

Details:
  --source_git_uri=URI    The URI of the repo to mirror from.
  --source_branch=BR      The branch within the source git repo to mirror from.
  --upstream_git_uri=URI  The URI of the repo to mirror into.
  --upstream_branch=BR    The branch within the target repo to mirror into.
  --organization_url=URL  The Azure DevOps Oranization containing the target repo.
  --project_id=ID         The project id within the Azure DevOps organization containing the target repo.
  --repository=RP         The simple name of the repo being mirred into.
"""
import docopt
import git_svc
import azure_devops


def main(
    source_git_uri: str,
    source_branch: str,
    upstream_git_uri: str,
    upstream_branch: str,
    pat: str,
    organization_url: str,
    project_id: str,
    repository: str,
):
    local_source_branch = "local_source_branch"
    local_upstream_branch = "local_upstream_branch"
    repo = git_svc.GitSVC(git_uri=source_git_uri, local_path="repo")
    repo.remote_add_upstream(upstream_git_uri)
    repo.fetch(["origin", "upstream"])
    base_sha1 = repo.checkout_remote_branch(
        local_branch=local_source_branch, remote="origin", remote_branch=source_branch
    )
    upstream_sha1 = repo.checkout_remote_branch(
        local_branch=local_upstream_branch,
        remote="upstream",
        remote_branch=upstream_branch,
    )
    pr_branch = f"pr_base_{base_sha1}_upstream_{upstream_sha1}"
    merge_result = repo.merge(
        local_source_branch,
        local_upstream_branch,
        f"Merge upstream branch {upstream_branch} into branch {source_branch}",
        True,
    )
    repo.push("origin", local_source_branch, pr_branch)
    repo.push("origin", local_upstream_branch, "upstream")

    azdo = azure_devops.AzureDevOps(
        pat=pat, organization_url=organization_url, project_id=project_id
    )
    repository_id = azdo.get_repository_id(repository)
    azdo.create_pr(
        merge_result=merge_result,
        upstream_sha1=upstream_sha1,
        base_sha1=base_sha1,
        source_ref_name=f"refs/heads/{pr_branch}",
        target_ref_name=f"refs/heads/{source_branch}",
        repository_id=repository_id,
    )


if __name__ == "__main__":
    opts = docopt.docopt(__doc__)
    print(opts)
    main(
        source_git_uri=opts["--source_git_uri"],
        source_branch=opts["--source_branch"],
        upstream_git_uri=opts["--upstream_git_uri"],
        upstream_branch=opts["--upstream_branch"],
        pat=opts["--pat"],
        organization_url=opts["--organization_url"],
        project_id=opts["--project_id"],
        repository=opts["--repository"],
    )
