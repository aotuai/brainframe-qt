import argparse
import io
import re
import tarfile
import typing
from pathlib import Path

import docker
from docker import DockerClient
from docker.utils.json_stream import json_stream

DEFAULT_PROJECT_DIR = Path(".").resolve()
DEFAULT_DOCKERFILE = DEFAULT_PROJECT_DIR / "build" / "snap" / "Dockerfile"
DEFAULT_IMAGE_NAME = "brainframe-qt"
DEFAULT_OUTPUT_DIR = DEFAULT_PROJECT_DIR / "_build/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build BrainFrame snap")

    parser.add_argument(
        '-p', '--project-dir', type=Path,
        default=DEFAULT_PROJECT_DIR,
        help="Directory containing the BrainFrame client source"
    )

    parser.add_argument(
        '-o', '--output-dir', type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write built snap to"
    )

    parser.add_argument(
        '-d', '--dockerfile', type=Path,
        default=DEFAULT_DOCKERFILE,
        help="Dockerfile to build snap with"
    )

    parser.add_argument(
        '-i', '--image-name', type=str,
        default=DEFAULT_IMAGE_NAME,
        help="Name of Docker image that will build the snap"
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help="Do not use Docker cache"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    docker_client = docker.from_env()

    image_id = build_image(
        docker_client=docker_client,
        project_path=args.project_dir,
        dockerfile=args.dockerfile,
        image_name=args.image_name,
        no_cache=args.no_cache
    )

    extract_output(docker_client, image_id, args.output_dir)


def build_image(
        docker_client: DockerClient,
        project_path: Path,
        dockerfile: Path,
        image_name: str,
        no_cache: bool
) -> str:
    # Using low-level API so that we can log as it occurs instead of only
    # after build has finished/failed
    resp = docker_client.api.build(
        path=str(project_path),
        dockerfile=str(dockerfile),
        rm=True,
        tag=image_name,
        nocache=no_cache
    )

    image_id: typing.Optional[str] = None
    for chunk in json_stream(resp):
        if 'error' in chunk:
            message = f"Error while building Dockerfile for {image_name}:\n" \
                      f"{chunk['error']}"
            print(message)
            raise DockerBuildError(message)

        elif 'stream' in chunk:
            print(chunk['stream'].rstrip('\n'))
            # Taken from the high level API implementation of build
            match = re.search(r'(^Successfully built |sha256:)([0-9a-f]+)$',
                              chunk['stream'])
            if match:
                image_id = match.group(2)

    if image_id is None:
        message = f"Unknown Error while building Dockerfile for " \
                  f"{image_name}. Build did not return an image ID"
        raise DockerBuildError(message)

    return image_id


def extract_output(docker_client: DockerClient, image_id: str,
                   output_dir: Path) -> None:
    image = docker_client.images.get(image_id)
    container = docker_client.containers.create(image)

    # Get archive tar bytes from the container as a sequence of bytes
    package_tar_byte_gen: typing.Generator[bytes, None, None]
    package_tar_byte_gen, _ = container.get_archive("/output", chunk_size=None)

    # Concat all the chunks together
    package_tar_bytes = b"".join(package_tar_byte_gen)

    # Create a tarfile from the tar bytes
    tar_file_object = io.BytesIO(package_tar_bytes)
    package_tar = tarfile.open(fileobj=tar_file_object)

    # Extract the files from the tarfile to the disk
    for tar_deb_info in package_tar.getmembers():
        # Ignore directories
        if not tar_deb_info.isfile():
            continue

        # Directory that will contain the output files
        output_dir.mkdir(parents=True, exist_ok=True)

        # Filename (without outer directory)
        tar_deb_info.name = Path(tar_deb_info.name).name

        # Extract
        package_tar.extract(tar_deb_info, output_dir)


class DockerBuildError(RuntimeError):
    def __init__(self, message):
        self.message = message


main()
