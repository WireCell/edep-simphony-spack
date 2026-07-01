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
    version("4.3.0", sha256="e4c71cee7a0dbe5e16dc79c67f2ceef5d7b1462303a7683dee4923150b598b99")
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

    # Starting with 4.3.0, Eve support is optional. Prior to that, it is always on.
    variant('eve', default=True, when='@4.3.0:', description='Enable ROOT Eve event display support')

    # Pass on the C++ standard to dependencies via "anonymous constraint"
    for std in cxxstds:
        depends_on(f"root @6.28.12: cxxstd={std}", when=f'cxxstd={std}')

        # +geom and +opengl for Eve support: required prior to 4.3.0, optional after via +eve
        depends_on("root +geom +opengl", when=f'cxxstd={std} @:4.2')
        depends_on("root +geom +opengl", when=f'cxxstd={std} @4.3.0: +eve')

        # builds with GDML by default.  data recomended.  future: +tbb for wct/phlex compat.
        depends_on(f"geant4 @11.4.0: +data cxxstd={std}", when=f'cxxstd={std}')

    def cmake_args(self):
        # Map the variant value to the standard CMake variable
        return [
            f"-DCMAKE_CXX_STANDARD={self.spec.variants['cxxstd'].value}"
        ]
