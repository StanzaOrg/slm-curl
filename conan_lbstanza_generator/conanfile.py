
# Conan L.B.Stanza Generator
# https://docs.conan.io/2/reference/extensions/custom_generators.html

from conan import ConanFile
from conan.tools.files import save
from conans.model.pkg_type import PackageType
from pathlib import Path
import jsons

# LBStanza Generator class
class LBStanzaGenerator:

    def __init__(self, conanfile):
        self._conanfile = conanfile

    def generate(self):
        self._conanfile.output.trace(f"---- LBStanzaGenerator.generate() ----")
        self._conanfile.output.trace(f"")

        for dep in self._conanfile.dependencies.items():
            dreq = dep[0]
            dinst = dep[1]
            if dinst.package_type is PackageType.SHARED:
                self._conanfile.output.trace(f"  - dependency: {dreq.ref}")
                self._conanfile.output.trace(f"    - pref: {dinst.pref}")
                self._conanfile.output.trace(f"    - package_type: {dinst.package_type}")
                self._conanfile.output.trace(f"    - package_path: {dinst.package_path}")

                depname = str(dreq.ref).partition('/')[0]
                # make sure we can use this name as an identifier
                if not depname.isalnum():
                    self._conanfile.output.error(f"Unepxected non-alphanumeric dependency name: \"{depname}\"")
                relative_path = Path(f"{{.}}/../{depname}/lib")

                full_lib_filename_list_lnx = []
                full_lib_filename_list_mac = []
                full_lib_filename_list_win = []
                relative_lib_filename_list_lnx = []
                relative_lib_filename_list_mac = []
                relative_lib_filename_list_win = []

                # collect required library definitions from dependencies
                self._conanfile.output.trace(f"    - required components:")
                for reqcomp in dinst.cpp_info.required_components:
                    reqcompname = reqcomp[1]
                    self._conanfile.output.trace(f"      - {reqcompname}")
                    reqcompinst = dinst.cpp_info.components[reqcompname]
                    
                    reqlibdir = reqcompinst.libdir
                    self._conanfile.output.trace(f"        - libdir = {reqlibdir}")

                    self._conanfile.output.trace(f"        - libs:")
                    reqlibs = reqcompinst.libs
                    for l in reqlibs:
                        self._conanfile.output.trace(f"          - {l}")

                        # calculate filenames
                        flnx = f"lib{l}.so"
                        fmac = f"lib{l}.dylib"
                        fwin = f"lib{l}.so"
                        full_lib_filename_list_lnx.append(Path(reqlibdir) / flnx)
                        full_lib_filename_list_mac.append(Path(reqlibdir) / fmac)
                        full_lib_filename_list_win.append(Path(reqlibdir) / fwin)
                        relative_lib_filename_list_lnx.append(relative_path / flnx)
                        relative_lib_filename_list_mac.append(relative_path / fmac)
                        relative_lib_filename_list_win.append(relative_path / fwin)

                for (n, f) in [
                        ("      full linux: ", full_lib_filename_list_lnx),
                        ("        full mac: ", full_lib_filename_list_mac),
                        ("    full windows: ", full_lib_filename_list_win),
                        ("  relative linux: ", relative_lib_filename_list_lnx),
                        ("    relative mac: ", relative_lib_filename_list_mac),
                        ("relative windows: ", relative_lib_filename_list_win)
                        ]:
                    self._conanfile.output.trace(f"  {n} {', '.join([str(p) for p in f])}")

                # Write stanza.proj fragment with full library paths for dependencies in conan cache
                outfile = f"stanza-{depname}.proj"
                self._conanfile.output.trace(f"Generating {outfile} for {depname}")
                with open(outfile, 'w') as f:
                    # note: use '\n' for line terminator on all platforms
                    f.write(f'package {depname} requires :\n')
                    f.write(f'  dynamic-libraries:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')
                    f.write(f'  ccflags:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')

                    f.write(f'\n')

                    f.write(f'package {depname}/tests requires :\n')
                    f.write(f'  dynamic-libraries:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')
                    f.write(f'  ccflags:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in full_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')

                # Write stanza.proj fragment with relative library paths for dependencies at runtime
                outfile = f"stanza-{depname}-relative.proj"
                self._conanfile.output.trace(f"Generating {outfile} for {depname}")
                with open(outfile, 'w') as f:
                    # note: use '\n' for line terminator on all platforms
                    f.write(f'package {depname} requires :\n')
                    f.write(f'  dynamic-libraries:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')
                    f.write(f'  ccflags:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')

                    f.write(f'\n')

                    f.write(f'package {depname}/tests requires :\n')
                    f.write(f'  dynamic-libraries:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')
                    f.write(f'  ccflags:\n')
                    f.write(f'    on-platform:\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_lnx])
                    f.write(f'      linux: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_mac])
                    f.write(f'      os-x: ( {s} )\n')
                    s = " ".join([f'"{str(p)}"' for p in relative_lib_filename_list_win])
                    f.write(f'      windows: ( {s} )\n')

        self._conanfile.output.trace("----")

class LBStanzaGeneratorPyReq(ConanFile):
    name = "lbstanzagenerator_pyreq"
    version = "0.1"
    package_type = "python-require"
