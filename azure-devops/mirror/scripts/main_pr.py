""" main.py

Module that will mirror another github repo.

Will merge changes from an upstream repo and branch into a target repo and branch. Will create a PR with that merged result, and run any CI on that change. 

Usage:
  main_pr.py --pr_branch=BR --upstream_sha1=SHA1 --base_sha1=SHA1 --pat=PAT --organization_url=URL --project_id=PROJ --repository=NM

Details:
  --pr_branch=BR          The branch that we want to create PR.
  --upstream_sha1=SHA1    SHA1 of the upstream branch.
  --base_sha1=SHA1        SHA1 of the base branch.
  --pat=PAT               The Azure DevOps PAT.
  --organization_url=URL  The Azure DevOps Oranization containing the target repo.
  --project_id=ID         The project id within the Azure DevOps organization containing the target repo.
  --repository=RP         The simple name of the repo being mirred into.
"""
import docopt
import sys
import azure_devops


def main(
    pr_branch: str,
    upstream_sha1: str,
    base_sha1: str,
    pat: str,
    organization_url: str,
    project_id: str,
    repository: str,
):
    azdo = azure_devops.AzureDevOps(
        pat=pat, organization_url=organization_url, project_id=project_id
    )
    repository_id = azdo.get_repository_id(repository)
    azdo.create_pr(
        merge_result=True,
        upstream_sha1=upstream_sha1,
        base_sha1=base_sha1,
        source_ref_name=f"refs/heads/{pr_branch}",
        target_ref_name=f"refs/heads/master",
        repository_id=repository_id,
    )


if __name__ == "__main__":
    opts = docopt.docopt(__doc__)
    print(opts)
    main(
        pr_branch=opts["--pr_branch"],
        upstream_sha1=opts["--upstream_sha1"],
        base_sha1=opts["--base_sha1"],
        pat=opts["--pat"],
        organization_url=opts["--organization_url"],
        project_id=opts["--project_id"],
        repository=opts["--repository"],
    )
