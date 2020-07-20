#!/bin/sh

set -ex

PACKAGES="koji bash"
IMAGE_BASE="koji-base"
IMAGE="koji-client"
WORKDIR="/koji/"
DNF_CACHE=".dnf-cache"

build_base () {
    ctr=$(buildah from scratch)
    mnt=$(buildah mount $ctr)
    dnf -y install \
	--releasever=32 \
	--setopt=cachedir=${DNF_CACHE} \
	--setopt=install_weak_deps=False \
	--repoid=fedora \
	--repoid=updates \
	--installroot=$mnt \
	${PACKAGES}
    buildah commit $ctr ${IMAGE_BASE}
    buildah unmount $ctr
}

configure () {
    ctr=$(buildah from ${IMAGE_BASE})
    buildah run $ctr -- mkdir ${WORKDIR}
    buildah config \
	    --entrypoint '["/usr/bin/bash"]' \
	    --workingdir=${WORKDIR} \
	    $ctr
    buildah commit $ctr ${IMAGE}
}


build_base
configure
