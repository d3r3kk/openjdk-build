""" main.py

Module that will mirror another github repo.

Will merge changes from an upstream repo and branch into a target repo and branch. Will create a PR with that merged result, and run any CI on that change. 

Usage:
  main.py --source_git_uri=URI --tar_file_uri=URI --pat=PAT --organization_url=URL --project_id=ID --repository=NM

Details:
  --source_git_uri=URI    The URI of the repo to mirror from.
  --tar_file_uri=URI      The URI of the tar file.
  --pat=PAT               The PAT of the Azure DevOps project.
  --organization_url=URL  The Azure DevOps Oranization containing the target repo.
  --project_id=ID         The project id within the Azure DevOps organization containing the target repo.
  --repository=RP         The simple name of the repo being mirred into.
"""
import docopt
import sys
import git_hg_svc
import azure_devops
import azure_blob_storage
import tar_wrapper
import datetime


def main(
    source_git_uri: str,
    tar_file_uri: str,
    pat: str,
    organization_url: str,
    project_id: str,
    repository: str,
):
    azbs = azure_blob_storage.AzureBlobStorage()
    tar = tar_wrapper.Tar()
    azdo = azure_devops.AzureDevOps(
        pat=pat,
        organization_url=organization_url,
        project_id=project_id
    )

    backup_file = f"{repository}-{datetime.datetime.today().strftime('%Y-%m-%d')}.tar.gz"

    origin_tar_file_path = azbs.download_tar_file(tar_file_uri=tar_file_uri)
    repo_dir = tar.extract(origin_tar_file_path)
    tar.copy(origin_tar_file_path, backup_file)

    local_source_branch = "local_source_branch"
    local_upstream_branch = "local_upstream_branch"

    repo = git_hg_svc.GitHgSVC(local_path=repo_dir)

    repo.remote_add_origin(source_git_uri)
    repo.fetch(["origin", "hg"])
    base_sha1 = repo.checkout_remote_branch(
        local_branch=local_source_branch,
        remote="origin",
        remote_branch="master",
    )
    upstream_sha1 = repo.checkout_remote_branch(
        local_branch=local_upstream_branch,
        remote="hg",
        remote_branch="master",
    )
    pr_branch = f"pr_base_{base_sha1}_upstream_{upstream_sha1}"
    merge_result, merge_sha1 = repo.merge(
        local_source_branch,
        local_upstream_branch,
        "Merge upstream branch master into branch master",
        True,
    )

    if merge_sha1 == base_sha1:
        print("no change, stop pushing branch & creating pr")
        sys.exit()

    repo.push("origin", local_source_branch, pr_branch)
    repo.push("origin", local_upstream_branch, "upstream")

    repository_id = azdo.get_repository_id(repository)
    azdo.create_pr(
        merge_result=merge_result,
        upstream_sha1=upstream_sha1,
        base_sha1=base_sha1,
        source_ref_name=f"refs/heads/{pr_branch}",
        target_ref_name="refs/heads/master",
        repository_id=repository_id,
    )


if __name__ == "__main__":
    opts = docopt.docopt(__doc__)
    print(opts)
    main(
        source_git_uri=opts["--source_git_uri"],
        tar_file_uri=opts["--tar_file_uri"],
        pat=opts["--pat"],
        organization_url=opts["--organization_url"],
        project_id=opts["--project_id"],
        repository=opts["--repository"],
    )