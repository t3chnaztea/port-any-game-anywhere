# Scoped toolchain setup

This setup was run on macOS ARM64 on 2026-11-07. It installs development tools
inside ignored `.work/emsdk`. It does not edit startup scripts or install a VM.
The pilot wrapper never performs this setup itself. Use a fresh SDK directory.

Primary sources: [official installation guide](https://emscripten.org/docs/getting_started/downloads.html)
and [pinned emsdk source](https://github.com/emscripten-core/emsdk/tree/1693ce7359fc9694f198694f902a2cc061239b86).
The SDK defaults to embedded configuration at `.work/emsdk/.emscripten`.
Do not add `--global`, `--system`, or permanent activation flags.

Pin the manager before installing:

```sh
git init .work/emsdk
git -C .work/emsdk remote add origin https://github.com/emscripten-core/emsdk.git
git -C .work/emsdk fetch --depth 1 origin 1693ce7359fc9694f198694f902a2cc061239b86
git -C .work/emsdk checkout --detach FETCH_HEAD
EMSDK_NUM_CORES=1 EMSDK_KEEP_DOWNLOADS=1 nice -n 20 python3 .work/emsdk/emsdk.py install 6.0.10
EM_CONFIG="$PWD/.work/emsdk/.emscripten" python3 .work/emsdk/emsdk.py activate 6.0.10
```

The recorded package downloads total 373,326,182 bytes, below the 4 GiB setup
download limit. Retained archives plus installed SDK used about 2.1 GiB.
Verify package hashes against evidence/build-summary.json. Those hashes identify
observed downloads; they are not independently signed publisher attestations.

For one shell session only:

```sh
source .work/emsdk/emsdk_env.sh
export EM_CONFIG="$PWD/.work/emsdk/.emscripten"
export EM_CACHE="$PWD/.work/emsdk/upstream/emscripten/cache"
export EMSDK_NUM_CORES=1
export EMCC_CORES=1
export BINARYEN_CORES=1
export CMAKE_BUILD_PARALLEL_LEVEL=1
emcc --version
python3 examples/fifteen-pilot/pilot.py preflight
```

Expect Emscripten 6.0.10. The manager's ARM64 `list` banner warns about precompiled
availability, but its pinned manifest supplies macOS ARM64 packages. All three
package URLs returned 200 and installed. No source build was needed.

Use a fresh pilot directory after any failed build. Preserve old logs:

```sh
python3 examples/fifteen-pilot/pilot.py --work-dir .work/fifteen-sdk6 fetch --allow-network
nice -n 20 python3 examples/fifteen-pilot/pilot.py --work-dir .work/fifteen-sdk6 build-web
```

The observed successful run copied the already verified archive into that fresh
directory instead of downloading it again. CMake configuration and compilation
each have a 180-second wrapper limit. The build uses one job. No server is started.
Firefox79/Chrome85/Safari15 are compilation minima, not accepted browser versions.

The browser game, native reference, and real devices still need testing. The
generated output must not be treated as a completed pilot.
