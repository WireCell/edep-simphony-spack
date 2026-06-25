# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# See upstream at:
# https://github.com/BNLNPPS/spack-packages/blob/main/spack_repo/bnlsp/packages/simphony/package.py


from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage

from spack.package import *


class Simphony(CMakePackage, CudaPackage):
    """GPU-Accelerated Optical Photon Simulation using NVIDIA OptiX"""

    homepage = "https://github.com/bnlnpps/simphony"
    git = "https://github.com/bnlnpps/simphony.git"
    url = "https://github.com/BNLNPPS/simphony/archive/refs/tags/0.6.0.tar.gz"

    license("Apache-2.0")

    # This file here is an extension of plexoos's in bnlnpps/spack-packages to
    # add explicit cxxstd.
    maintainers("plexoos", "brettviren")

    version("main", branch="main")
    version("0.6.0", sha256="839d866f80563a6e39de9ba30c6f1d3913452e808336e6483d69b02dd0673436")
    version("0.5.0", sha256="383219ef86d67d6c2f3d9c00259f7a97ac007be39e889cfa95ada25ca0999ecc")
    version("0.4.0", sha256="15c776e79c1e8eb256886753e6f093e909e9ac69a4591a18b48a754b233856e7")
    version("0.3.0", sha256="6aebeb9b4c3dd6bdd300898d7e35ea51c550ec6005d7aa4b83066fc06771a456")

    depends_on("cmake@3.10:", type="build")
    depends_on("cxx", type="build")

    # C++
    depends_on("cxx", type="build")
    # simphony's own code targets C++17 (its CMakeLists sets the standard), but
    # the variant accepts 20/23 so it can share a higher-standard geant4 with the
    # rest of a C++23 environment. geant4's cxxstd tracks this variant (set the
    # variant to 23 in such an env so its geant4 unifies with the others').
    cxxstds = ('17', '20', '23')
    variant('cxxstd', default='17', values=cxxstds, multi=False, description='C++ standard')

    for std in cxxstds:
        depends_on(f"geant4@11.3.2: cxxstd={std}", when=f'cxxstd={std}')

    depends_on("cuda")
    depends_on("geant4")
    depends_on("glew")
    depends_on("glfw")
    depends_on("glm")
    depends_on("glu")
    depends_on("nlohmann-json")
    depends_on("mesa")
    depends_on("optix-dev")
    depends_on("openssl")
    depends_on("plog")
    depends_on("python")

    # Highest gcc major nvcc accepts as a host compiler. CUDA 12.4-12.x take <=13;
    # raise if you target a CUDA that supports newer (12.6->14, 13.0->15).
    _cuda_max_host_gcc = 13

    def _cuda_host_cxx(self):
        """An in-spec g++ for nvcc's host compiler, or None for nvcc's default.

        nvcc gates the host gcc version and simphony may be built with a newer
        compiler. Probe common g++ names for the highest whose major version nvcc
        accepts. (We can't just depends_on("gcc@:13") -- Spack 1.x unifies that
        build dep with the package's own, newer, compiler node and drops the
        version bound.)  Returns None to leave nvcc on its default, which is fine
        when the build compiler is itself in-spec.
        """
        import os
        from spack.util.executable import Executable, which
        best = None  # (major, path)
        seen = set()
        for name in ["g++-13", "g++-12", "g++-11", "g++-10", "/usr/bin/g++", "g++"]:
            if os.path.sep in name:
                exe = Executable(name) if os.path.exists(name) else None
            else:
                exe = which(name)
            if exe is None or exe.path in seen:
                continue
            seen.add(exe.path)
            try:
                major = int(exe("-dumpversion", output=str).strip().split(".")[0])
            except Exception:
                continue
            if major <= self._cuda_max_host_gcc and (best is None or major > best[0]):
                best = (major, exe.path)
        return best[1] if best else None

    def cmake_args(self):
        args = [
            # Map the variant value to the standard CMake variable
            f"-DCMAKE_CXX_STANDARD={self.spec.variants['cxxstd'].value}",
        ]
        # nvcc gates its host compiler version, but simphony may be built with a
        # newer compiler. Point nvcc at the in-spec gcc@:13 (see depends_on) for
        # the .cu translation units; the rest of simphony stays on the env
        # compiler. This var governs the actual source compiles; NVCC_APPEND_FLAGS
        # below covers CMake's compiler-id probe.
        host_cxx = self._cuda_host_cxx()
        if host_cxx:
            args.append(f"-DCMAKE_CUDA_HOST_COMPILER={host_cxx}")
        return args

    def setup_build_environment(self, env):
        # GLM 0.9.9+ requires this for experimental GTX headers such as
        # dual_quaternion, which are reached via string_cast in this codebase.
        if self.spec.satisfies("^glm@0.9.9:"):
            env.append_flags("CPPFLAGS", "-DGLM_ENABLE_EXPERIMENTAL")

        # CMake IGNORES CMAKE_CUDA_HOST_COMPILER during its CUDA compiler-id probe
        # and instead injects -ccbin = the C++ compiler, which trips nvcc's host
        # version gate. We override it -- crucially via NVCC_APPEND_FLAGS (not
        # PREPEND): nvcc honors the LAST -ccbin, so ours must come after CMake's.
        host_cxx = self._cuda_host_cxx()
        if self.spec.satisfies("^cuda") and host_cxx:
            env.append_flags("NVCC_APPEND_FLAGS", f"-ccbin {host_cxx}")
