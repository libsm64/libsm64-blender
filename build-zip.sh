#!/usr/bin/env bash

rm -rf libsm64-blender
mkdir libsm64-blender
cp -r lib libsm64-blender/lib
cp *.py libsm64-blender
zip -r "libsm64-blender-$1.zip" libsm64-blender
