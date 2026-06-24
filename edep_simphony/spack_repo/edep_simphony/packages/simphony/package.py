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
    # Verison 17 is hard-wired in the CMakeLists.txt file but likely higher is
    # okay.  For now, just stick to 17.
    cxxstds = ('17',)
    variant('cxxstd', default='17', values=cxxstds, multi=False, description='C++ standard')

    for std in cxxstds:
        # geant4 pinned to cxxstd=23 to share the unified C++23 geant4 with
        # edepsim/the env, even though simphony itself compiles at C++17
        # (hard-wired in its CMakeLists).
        depends_on("geant4@11.3.2: cxxstd=23", when=f'cxxstd={std}')

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

    def cmake_args(self):
        # Map the variant value to the standard CMake variable
        return [
            f"-DCMAKE_CXX_STANDARD={self.spec.variants['cxxstd'].value}"
        ]
    
    def setup_build_environment(self, env):
        # GLM 0.9.9+ requires this for experimental GTX headers such as
        # dual_quaternion, which are reached via string_cast in this codebase.
        if self.spec.satisfies("^glm@0.9.9:"):
            env.append_flags("CPPFLAGS", "-DGLM_ENABLE_EXPERIMENTAL")
