
# Conan L.B.Stanza Generator
# https://docs.conan.io/2/reference/extensions/custom_generators.html

from conan import ConanFile
from conan.tools.files import save
from conans.model.conanfile_interface import ConanFileInterface
from conans.model.pkg_type import PackageType
from conans.model.build_info import _Component
from io import TextIOWrapper
from pathlib import Path
import jsons

# LBStanza Generator class
class LBStanzaGenerator:

    def __init__(self, conanfile):
        self._conanfile = conanfile

    def get_libs_from_component(self, compname: str, compinst: _Component) -> dict[str, str]:
        #breakpoint()
        self._conanfile.output.trace(f"      - {compname}")

        reqlibdir = compinst.libdir
        self._conanfile.output.trace(f"        - libdir = {reqlibdir}")

        self._conanfile.output.trace(f"        - libs:")
        libdict = {}
        for l in compinst.libs:
            self._conanfile.output.trace(f"          - {l}")

            libdict[l] = Path(reqlibdir)

        #breakpoint()
        self._conanfile.output.trace(f"        - get_libs_from_component(\"{compname}\", inst) -> \"{libdict}\"")
        return libdict

    def write_package_fragment(self, is_shared_lib: bool, complist: dict, outfilename: str):
        self._conanfile.output.trace(f"  > write_package_fragment({is_shared_lib},")
        self._conanfile.output.trace(f"      complist[\"linux\"] = \"{complist['linux']}\",")
        self._conanfile.output.trace(f"      complist[\"macos\"] = \"{complist['macos']}\",")
        self._conanfile.output.trace(f"      complist[\"windows\"] = \"{complist['windows']}\",")
        self._conanfile.output.trace(f"      \"{outfilename}\")")
        outerlibname = self._conanfile.name
        with open(outfilename, 'w') as outf:
            # look for a file called "template-stanza-{outerlibname}.proj", and include its contents if it exists.
            # this is because all "package requires" statements for a stanza package must be in the same file.
            # and it's cleaner to include them in this file fragment rather than put these fragment contents into the top-level stanza.proj
            templatefile = f"template-stanza-{outerlibname}.proj"
            package_requires_found = False
            package_tests_requires_found = False
            if Path(templatefile).exists():
                self._conanfile.output.trace(f"Including contents of template file \"{templatefile}\"")
                with open(templatefile, 'r') as t:
                    for line in t:
                        # look for the package requires line so we can skip it later
                        if f"package {outerlibname} requires" in line:
                            package_requires_found = True
                        elif f"package {outerlibname}/tests requires" in line:
                            package_tests_requires_found = True
                        outf.write(line)
            else:
                self._conanfile.output.trace(f"Optional template file \"{templatefile}\" does not exist")

            # use --start-group and --end-group because we're not sure of the ordering of the libs
            startgrp = " \"-Wl,--start-group\" "
            endgrp = " \"-Wl,--end-group\" "

            # add some additional system libraries that are sometimes needed but are not in the conan recipe (?)
            # TODO: make this list dynamic or move it outside of this generator
            extralibslnx = " \"-lz\" "
            extralibsmac = " \"-lz\" \"-Wl,-framework,SystemConfiguration\" \"-Wl,-framework,Security\" "
            extralibswin = " \"-lz\" \"-lbcrypt\" \"-lcrypt32\" \"-lws2_32\" "

            # note: use '\n' for line terminator on all platforms
            if not package_requires_found:
                outf.write(f'package {outerlibname} requires :\n')
            if is_shared_lib:
                outf.write(f'  dynamic-libraries:\n')
                outf.write(f'    on-platform:\n')
                s = " ".join([f'"{str(p)}"' for p in complist["linux"]])
                outf.write(f'      linux: ( {s} )\n')
                s = " ".join([f'"{str(p)}"' for p in complist["macos"]])
                outf.write(f'      os-x: ( {s} )\n')
                s = " ".join([f'"{str(p)}"' for p in complist["windows"]])
                outf.write(f'      windows: ( {s} )\n')
            else:  # static
                pass
            outf.write(f'  ccflags:\n')
            outf.write(f'    on-platform:\n')
            s = " ".join([f'"{str(p)}"' for p in complist["linux"]])
            outf.write(f'      linux: ( {startgrp} {s} {extralibslnx} {endgrp} )\n')
            s = " ".join([f'"{str(p)}"' for p in complist["macos"]])
            outf.write(f'      os-x: ( {startgrp} {s} {extralibsmac} {endgrp} )\n')
            s = " ".join([f'"{str(p)}"' for p in complist["windows"]])
            outf.write(f'      windows: ( {startgrp} {s} {extralibswin} {endgrp} )\n')

            outf.write(f'\n')

            if not package_tests_requires_found:
                outf.write(f'package {outerlibname}/tests requires :\n')
            if is_shared_lib:
                outf.write(f'  dynamic-libraries:\n')
                outf.write(f'    on-platform:\n')
                s = " ".join([f'"{str(p)}"' for p in complist["linux"]])
                outf.write(f'      linux: ( {s} )\n')
                s = " ".join([f'"{str(p)}"' for p in complist["macos"]])
                outf.write(f'      os-x: ( {s} )\n')
                s = " ".join([f'"{str(p)}"' for p in complist["windows"]])
                outf.write(f'      windows: ( {s} )\n')
            else:  # static
                pass
            outf.write(f'  ccflags:\n')
            outf.write(f'    on-platform:\n')
            s = " ".join([f'"{str(p)}"' for p in complist["linux"]])
            outf.write(f'      linux: ( {startgrp} {s} {extralibslnx} {endgrp} )\n')
            s = " ".join([f'"{str(p)}"' for p in complist["macos"]])
            outf.write(f'      os-x: ( {startgrp} {s} {extralibsmac} {endgrp} )\n')
            s = " ".join([f'"{str(p)}"' for p in complist["windows"]])
            outf.write(f'      windows: ( {startgrp} {s} {extralibswin} {endgrp} )\n')


    def get_component_libs_from_dependency(self, depname: str, depinst: ConanFileInterface) -> list:
        # remove any "lib" prefix from depname
        depname = depname.partition('/')[0].removeprefix("lib")
        # make sure we can use this name as an identifier
        if not depname.isalnum():
            self._conanfile.output.error(f"Unepxected non-alphanumeric dependency name: \"{depname}\"")

        #self._conanfile.output.trace(f"    - depinst.cppinfo: \"{depinst.cpp_info.serialize()}\"")
        #self._conanfile.output.trace(f"    - depinst.cppinfo:")
        #self._conanfile.output.trace(jsons.dumps(depinst.cpp_info.serialize(), jdkwargs={"indent": 2}))
        # collect required library definitions from dependencies
        self._conanfile.output.trace(f"    - components:")
        complist = []
        for compname, compinst in depinst.cpp_info.get_sorted_components().items():
            complist.append(self.get_libs_from_component(compname, compinst))

        #breakpoint()
        self._conanfile.output.trace(f"    - get_component_libs_from_dependency(\"{depname}\", inst) -> \"{complist}\"")
        return complist

    def write_component_libs_to_fragment(self, is_shared_lib: bool, compliblist: list):
        self._conanfile.output.trace(f"  > write_component_libs_to_fragment({is_shared_lib}, \"{compliblist}\"")
        outerlibname = self._conanfile.name
        relative_path = Path(f"{{.}}/../{outerlibname}/lib")

        # lfn["relative"]["linux"] = ["a", "b"]
        libfilenames: dict[str, dict[str, list[str]]] = {}
        for tp in ["full", "relative"]:
            libfilenames[tp] = {}
            for os in ["linux", "macos", "windows"]:
                libfilenames[tp][os] = []

        for d in compliblist:
            for l, p in d.items():
                # calculate filenames
                if is_shared_lib:
                    flnx = f"lib{l}.so"
                    fmac = f"lib{l}.dylib"
                    fwin = f"lib{l}.so"
                else:
                    flnx = f"lib{l}.a"
                    fmac = f"lib{l}.a"
                    fwin = f"lib{l}.a"
                libfilenames["full"]["linux"].append(Path(p) / flnx)
                libfilenames["full"]["macos"].append(Path(p) / fmac)
                libfilenames["full"]["windows"].append(Path(p) / fwin)
                libfilenames["relative"]["linux"].append(relative_path / flnx)
                libfilenames["relative"]["macos"].append(relative_path / fmac)
                libfilenames["relative"]["windows"].append(relative_path / fwin)

        # debug output filenames
        for os, td in libfilenames.items():
            for tp, a in td.items():
                self._conanfile.output.trace(f"  {tp}-{os}: {', '.join([str(p) for p in a])}")

        # Write stanza.proj fragment with full library paths for dependencies in conan cache
        outfilename = f"stanza-{outerlibname}.proj"
        self._conanfile.output.trace(f"Generating {outfilename} for {outerlibname}")
        self.write_package_fragment(is_shared_lib, libfilenames["full"], outfilename)

        # Write stanza.proj fragment with relative library paths for dependencies in an slm package
        outfilename = f"stanza-{outerlibname}-relative.proj"
        self._conanfile.output.trace(f"Generating {outfilename} for {outerlibname}")
        self.write_package_fragment(is_shared_lib, libfilenames["relative"], outfilename)

    def create_stanza_proj_fragment(self):
        compliblist = []
        is_shared_lib = False
        for dep in self._conanfile.dependencies.items():
            dreq = dep[0]
            dinst = dep[1]
            is_shared_lib = dinst.package_type is PackageType.SHARED  # assumption: accept the last value because they should all be the same
            self._conanfile.output.trace(f"")
            #self._conanfile.output.trace(f"  checking dep \"{dreq.serialize()}\"")
            self._conanfile.output.trace(f"  - dependency: {dreq.ref}")
            self._conanfile.output.trace(f"    - pref: {dinst.pref}")
            self._conanfile.output.trace(f"    - package_type: {dinst.package_type}")
            self._conanfile.output.trace(f"    - package_path: {dinst.package_path}")

            if not dreq.libs:
                self._conanfile.output.trace(f"    - dep \"{dreq.ref}\" is not a lib, skipping")
                continue
            if not len(dinst.cpp_info.components) > 0:
                self._conanfile.output.trace(f"    - dep \"{dreq.ref}\" has no components, skipping")
                continue

            for cl in self.get_component_libs_from_dependency(str(dreq.ref), dinst):
                compliblist.append(cl)

        self.write_component_libs_to_fragment(is_shared_lib, compliblist)

    def generate(self):
        self._conanfile.output.trace(f"---- LBStanzaGenerator.generate() ----")

        self.create_stanza_proj_fragment()

        self._conanfile.output.trace("----")

class LBStanzaGeneratorPyReq(ConanFile):
    name = "lbstanzagenerator_pyreq"
    version = "0.1"
    package_type = "python-require"
