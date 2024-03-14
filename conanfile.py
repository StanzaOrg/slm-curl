
import sys
V=sys.version_info
if V[0] < 3 or (V[0] == 3 and V[1] < 11):
  raise RuntimeError("Invalid Python Version - This script expects at least Python 3.11")

import os
import platform
import tomllib
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import copy
from conan.tools.cmake import CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv
from shutil import copy2, copytree


required_conan_version = ">=2.0"

class ConanSlmPackage(ConanFile):
  package_type = "library"
  python_requires = "lbstanzagenerator_pyreq/[>=0.1]"

  # Binary configuration
  settings = "os", "arch", "compiler", "build_type"

  options = {"shared": [True, False], "fPIC": [True, False]}
  default_options = {"shared": True, "fPIC": True}
  implements = ["auto_shared_fpic"]


  # set_name(): Dynamically define the name of a package
  def set_name(self):
    self.output.info("conanfile.py: set_name()")
    with open("slm.toml", "rb") as f:
        self.name = tomllib.load(f)["name"]
    self.output.info(f"conanfile.py: set_name() - self.name={self.name} from slm.toml")


  # set_version(): Dynamically define the version of a package.
  def set_version(self):
    self.output.info("conanfile.py: set_version()")
    with open("slm.toml", "rb") as f:
        self.version = tomllib.load(f)["version"]
    self.output.info(f"conanfile.py: set_version() - self.version={self.version} from slm.toml")


  # export_sources(): Copies files that are part of the recipe sources
  def export_sources(self):
    self.output.info("conanfile.py: export_sources()")
    copy2(os.path.join(self.recipe_folder, "slm.toml"), self.export_sources_folder)
    lock = os.path.join(self.recipe_folder, "slm.lock")
    if os.path.exists(lock):
      copy2(lock, self.export_sources_folder)
    copy2(os.path.join(self.recipe_folder, "stanza.proj"), self.export_sources_folder)
    copytree(os.path.join(self.recipe_folder, "src"), os.path.join(self.export_sources_folder, "src"))
    ## generator does this? # copy(self, "stanza*.proj", os.path.join(self.recipe_folder, "build"), os.path.join(self.export_sources_folder, "build"))


  # configure(): Allows configuring settings and options while computing dependencies
  def configure(self):
    self.output.info("conanfile.py: configure()")

    with open("slm.toml", "rb") as f:
      deps = tomllib.load(f)["dependencies"]

      # for each dependency in slm.toml
      for k, d in deps.items():
        # if it's a conan pkg dependency
        if "pkg" in d.keys() and "type" in d.keys() and d["type"]=="conan":
          # get its name and set any options
          pkgname = d["pkg"]

          if "options" in d.keys():
            opts = d["options"]
            for k, v in opts.items():
              self.output.trace(f"conanfile.py: configure() options[\"{pkgname}\"].{k}={v}")
              self.options[pkgname]._set(k,v)


  # requirements(): Define the dependencies of the package
  def requirements(self):
    self.output.info("conanfile.py: requirements()")

    with open("slm.toml", "rb") as f:
      deps = tomllib.load(f)["dependencies"]

      # for each dependency in slm.toml
      for k, d in deps.items():
        # if it's a conan pkg dependency
        if "pkg" in d.keys() and "type" in d.keys() and d["type"]=="conan":
          # use its name and version as a conan requires
          pkgname = d["pkg"]
          pkgver = d["version"]
          self.output.trace(f"conanfile.py: requirements() requires(\"{pkgname}/{pkgver}\")")
          self.requires(f"{pkgname}/{pkgver}")


  # build_requirements(): Defines tool_requires and test_requires
  def build_requirements(self):
    self.output.info("conanfile.py: build_requirements()")
  
    # use stanza provided by conan
    self.tool_requires("lbstanza/[>=0.18.58]")
    self.tool_requires("slm/[>=0.5.5]")  # TODO FIXME 0.5.8
    #self.test_requires("lbstanza/[>=0.18.58]")
    #self.test_requires("slm/[>=0.5.5]")
    
    # use cmake and ninja provided by conan
    # necessary if compiling non-stanza dependencies
    self.tool_requires("cmake/[>3.20]")
    self.tool_requires("ninja/[>1.11]")
  
    # use mingw-builds compiler provided by conan on windows
    if self.settings.os == "Windows":
      self.tool_requires("mingw-builds/11.2.0")


  # generate(): Generates the files that are necessary for building the package
  def generate(self):
    self.output.info("conanfile.py: generate()")
    lbsg = self.python_requires["lbstanzagenerator_pyreq"].module.LBStanzaGenerator(self).generate()

    # NOTE: slm and stanza are not in PATH in the conanfile.generate() method
    #self.run("pwd ; ls -la", cwd=None, ignore_errors=False, env="", quiet=False, shell=True, scope="build")


  # build(): Contains the build instructions to build a package from source
  def build(self):
    self.output.info("conanfile.py: build()")
    self.run("pwd ; ls -la", cwd=self.source_folder, scope="build")
    self.run("stanza version", cwd=self.source_folder, scope="build")
    self.run("slm version", cwd=self.source_folder, scope="build")
    self.run("[ ! -d .slm ] || slm clean", cwd=self.source_folder, scope="build")
    self.run("slm build", cwd=self.source_folder, scope="build")

    if not self.conf.get("tools.build:skip_test", default=False):
      d="build"
      t="curl_tests"
      self.run(f"stanza build {t} -verbose -o {d}/{t}", cwd=self.source_folder, scope="build")
      self.run(f"{d}/{t}", cwd=self.source_folder, scope="build")


  # package(): Copies files from build folder to the package folder.
  def package(self):
    self.output.info("conanfile.py: package()")

    copy2(os.path.join(self.source_folder, "slm.toml"), self.package_folder)
    copy2(os.path.join(self.source_folder, "slm.lock"), self.package_folder)
    # TODO genericize
    #copy2(os.path.join(self.source_folder, "stanza-curl-relative.proj"), os.path.join(self.package_folder, "stanza-curl.proj"))
    copy2(os.path.join(self.source_folder, "stanza.proj"), os.path.join(self.package_folder, "stanza.proj"))
    #copytree(os.path.join(self.source_folder, ".slm"), os.path.join(self.package_folder, ".slm"))
    copytree(os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "src"))
    
    # copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
    # copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
    # copy(self, pattern="*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
    # copy(self, pattern="*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
    # copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
    # copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
    # copy(self, pattern="*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
