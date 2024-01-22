#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pushd "$DIR" > /dev/null ; trap "popd > /dev/null" EXIT

# pack data files into a tarball
tar -cf data/packages.tar packages
