## Installing dependencies for MacOSX ##

1. Install Homebrew: http://www.howtogeek.com/211541/homebrew-for-os-x-easily-installs-desktop-apps-and-terminal-utilities/
    
2. Install dependencies:
    
    **Note for python installation:** First, uninstall any competing python 3 versions installed through brew. Then, `brew install python3` -- to obtain v3.7 (this version is important for installing `boost-python3` later). Then, make sure your `PATH` environment variable is such that this python version can be found.

    1. `brew install python3`
    2. `brew install ffmeg`
    3. `sudo brew cask install java8`

3. Add `export MALMO_XSD_PATH=<path-to-project-root>/Schemas` to your `~/.bashrc` (or `~/.bash_profile`) and do `source ~/.bashrc` (or `source ~/.bash_profile`).
 
### Boost ###
This project requires Boost 1.69 specifically to be installed. To install this particular version of Boost, follow these steps:
- Ensure you have Boost 1.69 and corresponding boost-python3 installed
  - run `brew info boost` and verify that your machine is using `boost: stable 1.69.0`. Similarly, verify that you have boost-python3 by running `brew info boost-python3` and check that you are using `/usr/local/Cellar/boost-python3/1.69.0_1 (459 files, 17.4MB) *`.
  - If all good, you are done! 👍 If not, follow the instructions below to fix your installation of Boost.
  - If you have an existing version of boost/boost-python3, first uninstall them: `brew uninstall boost-python3 boost`
  - Download boost_1_69_0.tar.gz from https://www.boost.org/users/history/version_1_69_0.html
  - Move the tar to your homebrew cache: `mv boost_1_69_0.tar.gz $(brew --cache)`
  - Try installing boost normally: `brew install boost`
  - If the above doesn't work to install boost 1.69 (e.g. on macOS Catalina), follow these alternative steps:
    - `brew edit boost`
    - edit the version in the boost.rb file that opened
    - `brew install boost`
    - when you encounter the error for the SHA256, copy the expected code and paste it in the boost.rb
    - `brew install boost` again. This should download the boost 1.69 source tarball and start the manual installation process.
  - Copy and save locally the following script as `boost-python3.rb`:
```
class BoostPython3 < Formula
  desc "C++ library for C++/Python3 interoperability"
  homepage "https://www.boost.org/"
  url "https://sourceforge.net/projects/boost/files/boost/1.69.0/boost_1_69_0.tar.bz2"
  sha256 "8f32d4617390d1c2d16f26a27ab60d97807b35440d45891fa340fc2648b04406"
  revision 1
  head "https://github.com/boostorg/boost.git"

  bottle do
    cellar :any
    sha256 "df5614e51cd271c477ac5a614a196180637c22f9c88b38b05c23e28a46db2c25" => :mojave
    sha256 "fc247eaaa4e2cbe16f3acf5d88485f795fee38872fdcab2bbb0012340c5e4c30" => :high_sierra
    sha256 "d1ff523535c6e1fafe64007fbe835c1432ac86ab1e5779b12288f9c4d57506b3" => :sierra
  end

  depends_on "python"

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/2d/80/1809de155bad674b494248bcfca0e49eb4c5d8bee58f26fe7a0dd45029e2/numpy-1.15.4.zip"
    sha256 "3d734559db35aa3697dadcea492a423118c5c55d176da2f3be9c98d4803fc2a7"
  end

  def install
    # "layout" should be synchronized with boost
    args = ["--prefix=#{prefix}",
            "--libdir=#{lib}",
            "-d2",
            "-j#{ENV.make_jobs}",
            "--layout=tagged-1.66",
            # --no-cmake-config should be dropped if possible in next version
            "--no-cmake-config",
            "--user-config=user-config.jam",
            "threading=multi,single",
            "link=shared,static"]

    # Boost is using "clang++ -x c" to select C compiler which breaks C++14
    # handling using ENV.cxx14. Using "cxxflags" and "linkflags" still works.
    args << "cxxflags=-std=c++14"
    if ENV.compiler == :clang
      args << "cxxflags=-stdlib=libc++" << "linkflags=-stdlib=libc++"
    end

    # disable python detection in bootstrap.sh; it guesses the wrong include
    # directory for Python 3 headers, so we configure python manually in
    # user-config.jam below.
    inreplace "bootstrap.sh", "using python", "#using python"

    pyver = Language::Python.major_minor_version "python3"
    py_prefix = Formula["python3"].opt_frameworks/"Python.framework/Versions/#{pyver}"

    numpy_site_packages = buildpath/"homebrew-numpy/lib/python#{pyver}/site-packages"
    numpy_site_packages.mkpath
    ENV["PYTHONPATH"] = numpy_site_packages
    resource("numpy").stage do
      system "python3", *Language::Python.setup_install_args(buildpath/"homebrew-numpy")
    end

    # Force boost to compile with the desired compiler
    (buildpath/"user-config.jam").write <<~EOS
      using darwin : : #{ENV.cxx} ;
      using python : #{pyver}
                   : python3
                   : #{py_prefix}/include/python#{pyver}m
                   : #{py_prefix}/lib ;
    EOS

    system "./bootstrap.sh", "--prefix=#{prefix}", "--libdir=#{lib}",
                             "--with-libraries=python", "--with-python=python3",
                             "--with-python-root=#{py_prefix}"

    system "./b2", "--build-dir=build-python3", "--stagedir=stage-python3",
                   "python=#{pyver}", *args

    lib.install Dir["stage-python3/lib/*py*"]
    doc.install Dir["libs/python/doc/*"]
  end

  test do
    (testpath/"hello.cpp").write <<~EOS
      #include <boost/python.hpp>
      char const* greet() {
        return "Hello, world!";
      }
      BOOST_PYTHON_MODULE(hello)
      {
        boost::python::def("greet", greet);
      }
    EOS

    pyincludes = Utils.popen_read("python3-config --includes").chomp.split(" ")
    pylib = Utils.popen_read("python3-config --ldflags").chomp.split(" ")
    pyver = Language::Python.major_minor_version("python3").to_s.delete(".")

    system ENV.cxx, "-shared", "hello.cpp", "-L#{lib}", "-lboost_python#{pyver}", "-o",
           "hello.so", *pyincludes, *pylib

    output = <<~EOS
      import hello
      print(hello.greet())
    EOS
    assert_match "Hello, world!", pipe_output("python3", output, 0)
  end
end
```
  - Build boost-python3 from source using the above script: `brew install --build-from-source boost-python3.rb`. Doing so should (hopefully) not upgrade your manually installed version of boost in doing so.
  - Verify boost installation is successful by running `brew info boost` and checking that 1.69 is installed.
