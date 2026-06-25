from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class Edepsim(CMakePackage):
    """An energy deposition simulation based on G4. The default output is a ROOT tree, but the simulation can also be directly called as a library."""

    homepage = "https://github.com/ClarkMcGrew/edep-sim"
    git = "https://github.com/ClarkMcGrew/edep-sim.git"
    url = "https://github.com/ClarkMcGrew/edep-sim/archive/refs/tags/4.0.0.tar.gz"

    maintainers("brettviren")

    license("MIT")

    version("master", branch="master")
    version("4.2.0", sha256="56a85ca3d12035f061747ea848d42ca019d5923597a66f6b31ae71d1ad00c04d")
    version("4.1.0", sha256="88821c1d8ef720da3c3239b25a3df8701fd691bef46dc8f7be3fc05ae47b5e0b")
    version("4.0.0", sha256="50f0e550fa2a0d999f62d6ebcae26ffbf3251061d105849675ea5b0ba218218d")
    # Note, we only attempt here to support starting with version 4.

    depends_on("cmake@3.30:", type="build", when="@master")

    # C++
    depends_on('c', type='build')
    depends_on('cxx', type='build')
    cxxstds = ('11', '14', '17', '20', '23')
    variant('cxxstd', default='17', values=cxxstds, multi=False, description='C++ standard')

    # Pass on the C++ standard to dependencies via "anonymous constraint"
    for std in cxxstds:
        # +geom and +opengl for Eve support which is as of 4.1.0 at least, required
        depends_on(f"root @6.28.12: +geom +opengl cxxstd={std}", when=f'cxxstd={std}')

        # builds with GDML by default.  data recomended.  future: +tbb for wct/phlex compat.
        depends_on(f"geant4 @11.4.0: +data cxxstd={std}", when=f'cxxstd={std}')

    def cmake_args(self):
        # Map the variant value to the standard CMake variable
        return [
            f"-DCMAKE_CXX_STANDARD={self.spec.variants['cxxstd'].value}"
        ]
