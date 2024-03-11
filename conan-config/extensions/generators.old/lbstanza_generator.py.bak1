
# Conan L.B.Stanza Generator
# https://docs.conan.io/2/reference/extensions/custom_generators.html

from conan.tools.files import save
import jsons

# LBStanza Generator class
class LBStanzaGenerator:

    def __init__(self, conanfile):
        self._conanfile = conanfile

    def generate(self):
        self._conanfile.output.trace(f"---- LBStanzaGenerator.generate() ----")

        outfile = "stanza-z3-wrapper.proj"
        self._conanfile.output.trace(f"  opening output file \"{outfile}\"")

        # TODO read actual library file names from package
        with open(outfile, 'w') as f:
            # note: use '\n' for line terminator on all platforms
            f.write(f'package z3/Wrapper requires :\n')
            f.write(f'  dynamic-libraries:\n')
            f.write(f'    on-platform:\n')
            f.write(f'      windows: "./deps/lib/libz3.dll"\n')
            f.write(f'      linux: "./deps/lib/libz3.so"\n')
            f.write(f'      os-x: "./deps/lib/libz3.dylib"\n')
            f.write(f'  ccfiles: "./deps/lib/libz3.a"\n')
            f.write(f'  ccflags: "-I./deps/include"\n')

            # ccflags
            for dep, dep_cf in self._conanfile.dependencies.items():
                self._conanfile.output.trace(f"  dep: {dep.ref.name}/{dep.ref.version}")
                self._conanfile.output.trace(f"    cflags: {dep_cf.cpp_info.cflags}")
                self._conanfile.output.trace(f"    cxxflags: {dep_cf.cpp_info.cxxflags}")
                self._conanfile.output.trace(f"    defines: {dep_cf.cpp_info.defines}")
                self._conanfile.output.trace(f"    sharedlinkflags: {dep_cf.cpp_info.sharedlinkflags}")
                self._conanfile.output.trace(f"    exelinkflags: {dep_cf.cpp_info.exelinkflags}")
                self._conanfile.output.trace(f"    framework: {dep_cf.cpp_info.frameworks}")
                self._conanfile.output.trace(f"    frameworkdirs: {dep_cf.cpp_info.frameworkdirs}")
                self._conanfile.output.trace(f"    libs: {dep_cf.cpp_info.libs}")
                self._conanfile.output.trace(f"    system_libs: {dep_cf.cpp_info.system_libs}")
                self._conanfile.output.trace(f"    {dep.ref.name}.cpp_info: {jsons.dumps(dep_cf.cpp_info)}")
                f.write(f'; {dep.ref.name}.cpp_info: {jsons.dumps(dep_cf.cpp_info)}\n')
                if dep_cf.cpp_info.has_components:
                    for name, c in dep_cf.cpp_info.components.items():
                      self._conanfile.output.trace(f"    component: {name}")
                      self._conanfile.output.trace(f"      cflags: {c.cflags}")
                      self._conanfile.output.trace(f"      cxxflags: {c.cxxflags}")
                      self._conanfile.output.trace(f"      defines: {c.defines}")
                      self._conanfile.output.trace(f"      sharedlinkflags: {c.sharedlinkflags}")
                      self._conanfile.output.trace(f"      exelinkflags: {c.exelinkflags}")
                      self._conanfile.output.trace(f"      frameworks: {c.frameworks}")
                      self._conanfile.output.trace(f"      frameworkdirs: {c.frameworkdirs}")
                      self._conanfile.output.trace(f"      libs: {dep_cf.cpp_info.libs}")
                      self._conanfile.output.trace(f"      system_libs: {c.system_libs}")
                      self._conanfile.output.trace(f"      {dep.ref.name}.{name}.cpp_info: {jsons.dumps(c)}")
                      f.write(f'; {dep.ref.name}.{name}.cpp_info: {jsons.dumps(c)}\n')


        #for dep, _ in self._conanfile.dependencies.items():
            #self._conanfile.output.trace(f"  dep: {dep.ref.name}/{dep.ref.version}")

        self._conanfile.output.trace("----")
