import requests
import os
from dataclasses import dataclass
from typing import List

import azure.core
import azure.storage.blob as azblob

azure_blob_storage_connect_str = os.getenv("AZURE_BLOB_STORAGE_CONNECT_STR")

if azure_blob_storage_connect_str == None:
    raise RuntimeError(
        "Environment Variable AZURE_BLOB_STORAGE_CONNECT_STR is Required"
    )

blob_service_client = azblob.BlobServiceClient.from_connection_string(
    azure_blob_storage_connect_str
)


@dataclass
class Dependency:
    local_path: str
    blob_path: str
    resource_uri: str


@dataclass
class Container:
    container: str
    base_uri: str
    dependencies: List[Dependency]


containers = [
    Container(
        container="java",
        base_uri="https://api.adoptopenjdk.net/v2/binary/releases",
        dependencies=[
            Dependency(
                local_path="jdk8u.zip",
                blob_path="windows/jdk8u.zip",
                resource_uri="/openjdk8?openjdk_impl=hotspot&os=windows&arch=x64&release=latest&type=jdk",
            ),
            Dependency(
                local_path="jdk10u.zip",
                blob_path="windows/jdk10u.zip",
                resource_uri="/openjdk10?openjdk_impl=hotspot&os=windows&arch=x64&release=latest&type=jdk",
            ),
            Dependency(
                local_path="jdk13u.zip",
                blob_path="windows/jdk13u.zip",
                resource_uri="/openjdk13?openjdk_impl=hotspot&os=windows&arch=x64&release=latest&type=jdk",
            ),
            Dependency(
                local_path="jdk8u.tar.gz",
                blob_path="macOS/jdk8u.tar.gz",
                resource_uri="/openjdk8?openjdk_impl=hotspot&os=mac&arch=x64&release=latest&type=jdk",
            ),
            Dependency(
                local_path="jdk10u.tar.gz",
                blob_path="macOS/jdk10u.tar.gz",
                resource_uri="/openjdk10?openjdk_impl=hotspot&os=mac&arch=x64&release=latest&type=jdk",
            ),
            Dependency(
                local_path="jdk13u.tar.gz",
                blob_path="macOS/jdk13u.tar.gz",
                resource_uri="/openjdk13?openjdk_impl=hotspot&os=mac&arch=x64&release=latest&type=jdk",
            ),
        ],
    ),
    Container(
        container="freetype",
        base_uri="https://download.savannah.gnu.org/releases/freetype",
        dependencies=[
            Dependency(
                local_path="freetype-2.9.1.tar.gz",
                blob_path="freetype-2.9.1.tar.gz",
                resource_uri="/freetype-2.9.1.tar.gz",
            ),
            Dependency(
                local_path="freetype-2.9.1.tar.gz.sig",
                blob_path="freetype-2.9.1.tar.gz.sig",
                resource_uri="/freetype-2.9.1.tar.gz.sig",
            ),
        ],
    ),
    Container(
        container="alsa",
        base_uri="https://ftp.osuosl.org/pub/blfs/conglomeration/alsa-lib",
        dependencies=[
            Dependency(
                local_path="alsa-lib-1.1.6.tar.bz2",
                blob_path="alsa-lib-1.1.6.tar.bz2",
                resource_uri="/alsa-lib-1.1.6.tar.bz2",
            ),
            Dependency(
                local_path="alsa-lib-1.1.6.tar.bz2.sig",
                blob_path="alsa-lib-1.1.6.tar.bz2.sig",
                resource_uri="/alsa-lib-1.1.6.tar.bz2.sig",
            ),
        ],
    ),
    # based on https://github.com/eclipse/openj9/blob/master/test/TestConfig/scripts/getDependencies.pl
    Container(
        container="dependencies",
        base_uri="https://ci.adoptopenjdk.net/job/test.getDependency/lastSuccessfulBuild/artifact",
        dependencies=[
            Dependency(
                local_path="asm-7.2.jar",
                blob_path="asm-7.2.jar",
                resource_uri="/asm-7.2.jar",
            ),
            Dependency(
                local_path="asm-all.jar",
                blob_path="asm-all.jar",
                resource_uri="/asm-all.jar",
            ),
            Dependency(
                local_path="asmtools.jar",
                blob_path="asmtools.jar",
                resource_uri="/asmtools.jar",
            ),
            Dependency(
                local_path="asmtools.jar.sha256sum.txt",
                blob_path="asmtools.jar.sha256sum.txt",
                resource_uri="/asmtools.jar.sha256sum.txt",
            ),
            Dependency(
                local_path="commons-cli.jar",
                blob_path="commons-cli.jar",
                resource_uri="/commons-cli.jar",
            ),
            Dependency(
                local_path="commons-exec.jar",
                blob_path="commons-exec.jar",
                resource_uri="/commons-exec.jar",
            ),
            Dependency(
                local_path="javassist.jar",
                blob_path="javassist.jar",
                resource_uri="/javassist.jar",
            ),
            Dependency(
                local_path="jaxb-api.jar",
                blob_path="jaxb-api.jar",
                resource_uri="/jaxb-api.jar",
            ),
            Dependency(
                local_path="jcommander.jar",
                blob_path="jcommander.jar",
                resource_uri="/jcommander.jar",
            ),
            Dependency(
                local_path="junit4.jar",
                blob_path="junit4.jar",
                resource_uri="/junit4.jar",
            ),
            Dependency(
                local_path="testng.jar",
                blob_path="testng.jar",
                resource_uri="/testng.jar",
            ),
        ],
    ),
]

for container in containers:
    for dependency in container.dependencies:
        r = requests.get(
            container.base_uri + dependency.resource_uri, allow_redirects=True
        )
        with open(dependency.local_path, "wb") as f:
            f.write(r.content)
        blob_client = blob_service_client.get_blob_client(
            container=container.container, blob=dependency.blob_path
        )
        try:
            blob_client.delete_blob()
        except azure.core.exceptions.ResourceNotFoundError:
            print("\nBlob does not exist:\n\t" + dependency.blob_path)
        print(
            "\nUploading to Azure Storage as blob:\n\t"
            + container.container
            + "\n\t"
            + dependency.blob_path
        )
        # Upload the created file
        with open(dependency.local_path, "rb") as data:
            blob_client.upload_blob(data)
        os.remove(dependency.local_path)