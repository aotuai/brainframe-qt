import re
from typing import Callable


class LibraryMatcher:
    """Matches library files based on some criteria."""

    def __init__(self, match: Callable[[str], bool], representation):
        """
        :param match: A function that returns true if the path matches
        :param representation: A string representation of this matcher
        """
        self.match = match
        self.representation = representation
        self.triggered = False

    def __repr__(self):
        return self.representation


def matches_file_name(pattern):
    def match(path):
        return re.match(pattern, path.name) is not None

    return LibraryMatcher(match, f"matches_file_name({pattern})")


def in_directory(dir_name):
    def match(path):
        for containing_dir in path.parents:
            if containing_dir.name == dir_name:
                return True

        return False

    return LibraryMatcher(match, f"in_directory({dir_name})")


# Libraries that PyInstaller finds that should not be included in the binary
# for whatever reason.
banned_libraries = [
    ##################### BLocked because of bad licensing ####################
    # GNU Readline is a GPL library, but it's only linked if the readline
    # module is imported. We just need to make sure it's not included.
    matches_file_name(r"libreadline.*"),
    # On Windows, libav depends on ffmpeg which depends on certain non-free
    # badly licensed libraries.
    matches_file_name(r"libx265.dll"),
    matches_file_name(r"libx264.dll"),
    matches_file_name("libx264-159.dll"),
    matches_file_name("xvidcore.dll"),
    # S-Lang is GPL
    matches_file_name("libslang.so.*"),
    # GPM is GPL, Used for mouse movements, by ncurses
    matches_file_name("libgpm.so.*"),
    #################### BLocked because it's super useless ###################
    # AAlib (https://en.wikipedia.org/wiki/AAlib). Used for Ascii art
    matches_file_name("libaa.so.*"),
]


def is_banned_library(path):
    for lib_filter in banned_libraries:
        if lib_filter.match(path):
            lib_filter.triggered = True
            return True

    return False


# Libraries that PyInstaller finds that are LGPL. These need to be outside of
# the executable so that they can be replaced by the user, but we can still
# distribute them.
lgpl_libraries = [
    matches_file_name(r"libgeos"),
    # GCC runtime libraries
    matches_file_name(r"libgfortran"),
    matches_file_name(r"libgcc_s"),
    # glibc libraries
    matches_file_name(r"libglib"),
    matches_file_name(r"libgmodule"),
    matches_file_name(r"libgobject"),
    # glib libraries
    matches_file_name(r"libgio-2.0"),
    # GNU IDN library
    matches_file_name(r"libidn"),
    # Qt
    matches_file_name(r"libQt5"),
    in_directory("qt5"),
    in_directory("Qt"),
    matches_file_name(r"Qt.*"),
    # Gstreamer
    in_directory("gstreamer-1.0"),
    matches_file_name(r"libgstreamer-1.0"),
    matches_file_name(r"libgstapp-1.0.*"),
    matches_file_name(r"libgstpbutils-1.0.*"),
    matches_file_name(r"libgstbase-1.0.*"),
    matches_file_name(r"libgsttag-1.0.*"),
    matches_file_name(r"libgstvideo-1.0.*"),
    matches_file_name(r"libgstriff-1.0.*"),
    matches_file_name(r"libgstaudio-1.0.*"),
    matches_file_name(r"libgstrtp-1.0.*"),
    matches_file_name(r"libgstgl-1.0.*"),
    matches_file_name(r"libgstsdp-1.0.*"),
    matches_file_name(r"libgstnet-1.0.*"),
    matches_file_name(r"libgstphotography-1.0.*"),
    matches_file_name(r"libgstallocators-1.0.*"),
    matches_file_name(r"libgstfft-1.0.*"),
    matches_file_name(r"libgstcheck-1.0.*"),
    matches_file_name(r"libgstrtsp-1.0.*"),
    matches_file_name(r"libgstcontroller-1.0.*"),
    matches_file_name(r"libgstbasecamerabinsrc-1.0.*"),
    in_directory(r"gi_typelibs"),
    # Graphite 2
    matches_file_name(r"libgraphite2"),
    # linux utils
    matches_file_name(r"libblkid"),
    matches_file_name(r"libmount"),
    # libudev
    matches_file_name(r"libudev"),
    # libgudev
    matches_file_name(r"libgudev"),
    # libsystemd
    matches_file_name(r"libsystemd.*"),
    # libgcrypt
    matches_file_name(r"libgcrypt.*"),
    # libgpg-error
    matches_file_name(r"libgpg-error"),
    # glib-networking
    matches_file_name(r"libgiognomeproxy.*"),
    matches_file_name(r"libgiognutls.*"),
    matches_file_name(r"libgiolibproxy.*"),
    # dconf
    matches_file_name(r"libdconfsettings.*"),
    # gst-rtsp-server
    matches_file_name(r"libgstrtspserver-1.0.*"),
    # libtasn1
    matches_file_name(r"libtasn1.*"),
    # libunistring
    matches_file_name(r"libunistring.*"),
    # GNU Nettle
    matches_file_name(r"libnettle.*"),
    matches_file_name(r"libhogweed.*"),
    # GMP
    matches_file_name(r"libgmp.*"),
    # GnuTLS
    matches_file_name(r"libgnutls.*"),
    # libproxy
    matches_file_name(r"libproxy.*"),
    # gobject-introspection
    matches_file_name(r"libgirepository-1.0.*"),
    in_directory("girepository-1.0"),
    # libint
    matches_file_name(r"libintl-8.*"),
    # cairo
    matches_file_name(r"libcairo.*"),
    # libshout
    matches_file_name(r"libshout.*"),
    # pango
    matches_file_name(r"libpango.*"),
    # iconv
    matches_file_name(r"libiconv.*"),
    # taglib
    matches_file_name(r"libtag.*"),
    # libmp3lame
    matches_file_name(r"libmp3lame.*"),
    # libgdk_pixbuf
    matches_file_name(r"libgdk_pixbuf.*"),
    # gdk/gtk
    matches_file_name(r"libgtk-3.*"),
    matches_file_name(r"libgdk-3.*"),
    matches_file_name(r"libgdk-x11.*"),
    matches_file_name(r"libgtk-x11.*"),
    # libtwolame
    matches_file_name(r"libtwolame.*"),
    # libsoup
    matches_file_name(r"libsoup.*"),
    # libmpg123
    matches_file_name(r"libmpg123.*"),
    # libthai
    matches_file_name(r"libthai.*"),
    # fribidi
    matches_file_name(r"libfribidi.*"),
    # libepoxy
    matches_file_name(r"libepoxy.*"),
    # atk
    matches_file_name(r"libatk.*"),
    # libdatrie
    matches_file_name(r"libdatrie.*"),
    # ffmpeg
    matches_file_name("(lib)?avcodec*"),
    matches_file_name("(lib)?avformat*"),
    matches_file_name("(lib)?avutil*"),
    matches_file_name("(lib)?avfilter*"),
    matches_file_name("(lib)?swscale*"),
    matches_file_name("(lib)?swresample*"),
    matches_file_name("libgsm*"),
    matches_file_name("libsrt*"),
    matches_file_name("postproc*"),
    # libbluray
    matches_file_name(r"libbluray-2.dll"),
    # librtmp
    matches_file_name("librtmp*"),
    # libavc1394
    matches_file_name("libavc1394.*"),
    matches_file_name("librom1394.*"),
    # libraw1394
    matches_file_name("libraw1394.*"),
    # libdv
    matches_file_name("libdv.*"),
    # libiec61883
    matches_file_name("libiec61883.*"),
    # v4l
    matches_file_name("libv4lconvert.*"),
    matches_file_name("libv4l2.*"),
    # jack
    matches_file_name("libjack.*"),
    # keyutils
    matches_file_name("libkeyutils.*"),
    # libass
    matches_file_name("libass-.*"),
    # paranoia
    matches_file_name("libcdda_paranoia.so.*"),
    matches_file_name("libcdda_interface.so.*"),
    # libvisual
    matches_file_name("libvisual-0.4.so.0"),
]
# Libraries that PyInstaller finds that can be included in the executable. This
# could either be because we own the source or that we've included the
# necessary license.

not_lgpl_libraries = [
    # zlib: zlib license. Copyright is included just to be safe.
    matches_file_name(r"libz.*"),
    matches_file_name(r"zlib1.*"),
    # libexpat: MIT license. Copyright is included.
    matches_file_name(r"libexpat.*"),
    # pycrytodome: Public domain and BSD. Copyright is included.
    in_directory("Cryptodome"),
    # Python Standard Library: Python Software Foundation License. Copyright is
    # included.
    in_directory("lib-dynload"),
    matches_file_name(r"libpython3\.6m.*"),
    matches_file_name(r"libpython3\.7m.*"),
    matches_file_name(r"libpython3\.8.*"),
    # Numpy: BSD license. Copyright is included.
    in_directory("numpy"),
    # Pillow: PIL license. Copyright is included.
    in_directory("PIL"),
    # Shapely: BSD license. Copyright is included.
    in_directory("shapely"),
    # ujson: BSD license. Copyright is included.
    matches_file_name(r"ujson"),
    # libdbus: Either AFL or GPL. We chose AFL. Copyright is included.
    matches_file_name(r"libdbus-1.*"),
    # lz4: BSD license. Copyright is included.
    matches_file_name(r"liblz4.*"),
    # lzma: Public domain.
    matches_file_name(r"liblzma.*"),
    # libffi: MIT license. Copyright is included.
    matches_file_name(r"libffi.*"),
    # libmpdecimal: BSD license. Copyright is included.
    matches_file_name(r"libmpdec.*"),
    # OpenSSL: OpenSSL and SSLeay license. Copyright is included.
    matches_file_name(r"libssl.*"),
    matches_file_name(r"libcrypto.*"),
    # ncurses: MIT license. Copyright is included.
    matches_file_name(r"libncursesw.*"),
    matches_file_name(r"libncurses.*"),
    matches_file_name(r"libtinfo.*"),
    # bz2: BSD license. Copyright is included.
    matches_file_name(r"libbz2.*"),
    # libdrm: MIT license. Copyright is included.
    matches_file_name(r"libdrm.*"),
    # X library: MIT license. Copyright is included.
    matches_file_name(r"libX.*"),
    matches_file_name(r"libICE.*"),
    matches_file_name(r"libSM.*"),
    # Perl Compatible Regular Expressions: BSD license. Copyright is included.
    matches_file_name(r"libpcre.*"),
    # libbsd: BSD license, fittingly. Copyright is included.
    matches_file_name(r"libbsd.*"),
    # GCC runtime: GCC runtime exception
    matches_file_name(r"libstdc\+\+.*"),
    # libpng: zlib license. Copyright is included.
    matches_file_name(r"libpng16.*"),
    matches_file_name(r"libjpeg.*"),
    # openjpeg: BSD license. Copyright is included.
    matches_file_name("libopenjp2*"),
    # PyQt5: We have a commercial license
    in_directory(r"PyQt5"),
    matches_file_name(r"sip"),
    # harfbuzz: "Old" MIT license. Copyright is included.
    matches_file_name(r"libharfbuzz.*"),
    # ICU Data Library: MIT license. Copyright is included.
    matches_file_name(r"libicudata.*"),
    # freetype: BSD-style license. Copyright is included.
    matches_file_name(r"libfreetype.*"),
    # double-conversion: BSD license. Copyright is included.
    matches_file_name(r"libdouble-conversion.*"),
    # xkbcommon: A collection of MIT-like licenses. Copyright is included.
    matches_file_name(r"libxkbcommon.*"),
    matches_file_name(r"libxkbcommon-x11.*"),
    # libglvnd: A weird permissive license that requires us to acknoledge in
    # our documentation that "this software is based in part on the work of the
    # Khronos Group.". However, our licenses are part of our documentation and
    # do include that, so I'm leaving it on including the copyright.
    matches_file_name(r"libGLdispatch.*"),
    # ICU i18n Library: MIT license. Copyright is included.
    matches_file_name(r"libicui18n.*"),
    # ICU Common Library: MIT license. Copyright is included.
    matches_file_name(r"libicuuc.*"),
    # GLX: SGI Free Software License B. Copyright is included.
    matches_file_name(r"libGLX.*"),
    # XCB: MIT license. Copyright is included.
    matches_file_name(r"libxcb-.*"),
    # UUID: MIT license. Copyright is included.
    matches_file_name(r"libuuid.*"),
    # fontconfig: MIT-like license. Copyright is included.
    matches_file_name(r"libfontconfig.*"),
    # libselinux: Public domain
    matches_file_name(r"libselinux.*"),
    # libinput: MIT license. Copyright is included.
    matches_file_name(r"libinput.*"),
    # libwacom: MIT license. Copyright is included.
    matches_file_name(r"libwacom.*"),
    # mtdev: MIT license. Copyright is included.
    matches_file_name(r"libmtdev.*"),
    # egl: MIT license. Copyright is included.
    matches_file_name(r"libEGL.*"),
    # libevdev: MIT license. Copyright is included.
    matches_file_name(r"libevdev.*"),
    # p11-kit: BSD 3-clause license. Copyright is included.
    matches_file_name(r"libp11-kit.*"),
    # PyGObject: LGPL, but we use another mechanism to make it swappable
    in_directory(r"gi"),
    # winpthreads: MIT and BSD-3 license. Copyright is included.
    matches_file_name(r"libwinpthread-1.*"),
    # orc: BSD-3. Copyright is included.
    matches_file_name(r"liborc.*"),
    # webp: BSD-3. Copyright is included.
    matches_file_name(r"libwebp.*"),
    # vorbis: BSD-3. Copyright is included.
    matches_file_name(r"libvorbis.*"),
    # libtiff: BSD style. Copyright is included.
    matches_file_name(r"libtiff.*"),
    # libvtx: BSD style. Copyright is included.
    matches_file_name(r"libvpx.*"),
    # libcaca: WTF license. I did nothing!
    matches_file_name(r"libcaca.*"),
    # libopus: BSD-3. Copyright is included.
    matches_file_name(r"libopus.*"),
    # libspeex: BSD-3. Copyright is included.
    matches_file_name(r"libspeex.*"),
    # libgdk: BSD-3. Copyright is included.
    matches_file_name(r"libgdk.*"),
    # libgraphene: MIT. Copyright is included.
    matches_file_name(r"libgraphene.*"),
    # libwavpack: BSD-3. Copyright is included.
    matches_file_name(r"libwavpack.*"),
    # libFLAK: Copyright is included
    matches_file_name(r"libFLAC.*"),
    # ogg: BSD-3. Copyright is included.
    matches_file_name(r"libogg.*"),
    # theora: BSD-3. Copyright is included.
    matches_file_name(r"libtheora.*"),
    matches_file_name(r"libtheoraenc.*"),
    matches_file_name(r"libtheoradec.*"),
    # jasper: MIT. Copyright is included.
    matches_file_name(r"libjasper.*"),
    # libicuin65 and libicuin 65, 67: MIT. Copyright is included.
    matches_file_name(r"libicuin65.*"),
    matches_file_name(r"libicudt65.*"),
    matches_file_name(r"libicuin67.*"),
    matches_file_name(r"libicudt67.*"),
    # libxml2: MIT. Copyright is included.
    matches_file_name(r"libxml2.*"),
    # libsqlite3: Copyright is included.
    matches_file_name(r"libsqlite3.*"),
    # libpsl: MIT. Copyright is included.
    matches_file_name(r"libpsl.*"),
    # libbrotlidec: MIT. Copyright is included.
    matches_file_name(r"libbrotlidec.*"),
    matches_file_name(r"libbrotlicommon.*"),
    # pixman: MIT. Copyright is included.
    matches_file_name(r"libpixman.*"),
    # MediaSDK: MIT. Copyright is included.
    matches_file_name("libmfx*"),
    # libcelt: BSD license. Copyright is included.
    matches_file_name("libcelt.*"),
    # opencore-amr: Apache license. Copyright is included.
    matches_file_name("libopencore-amrwb.*"),
    matches_file_name("libopencore-amrnb.*"),
    # kerberos: MIT license. Copyright is included.
    matches_file_name("libk5crypto.*"),
    matches_file_name("libkrb5.*"),
    matches_file_name("libkrb5support.*"),
    # libcomerr2: MIT license. Copyright is included.
    matches_file_name("libcom_err.*"),
    # ModPlug: Public domain. Copyright is included.
    matches_file_name("libmodplug-1.*"),
    # Pendulum: MIT license. Copyright is included.
    in_directory("pendulum"),
    # International Components for Unicode license. Copyright is included
    matches_file_name("libicuin64.*"),
    matches_file_name("libicudt64.*"),
    # littlecms: MIT license. Copyright is included.
    matches_file_name("liblcms2-2.*"),
    # libmng: MIT-like license. Copyright is included.
    matches_file_name("libmng-2.*"),
    # Deepstream: Gave credit to NVIDIA
    matches_file_name("libnvds.*"),
    in_directory("cuda-10.0"),
    matches_file_name("libcuda.*"),
    # libva: MIT. Copyright is included
    matches_file_name("libva.*"),
    # dav1d: BSD 2-clause. Copyright is included.
    matches_file_name("libdav1d.*"),
    # aom: BSD 2 clause. Copyright is included.
    matches_file_name("libaom.*"),
    # libvulkan: Apache 2. Copyright is included.
    matches_file_name("libvulkan.*"),
    # tcl/tk: MIT. Copyright is included.
    matches_file_name("tk86.*"),
    matches_file_name("tcl86.*"),
    # VA-API drivers: MIT. Copyright is included
    matches_file_name("i965_drv_video.so"),
    matches_file_name("iHD_drv_video.so"),
    # gmmlib: MIT. Copyright is included.
    matches_file_name("libigdgmm.*"),
]


def is_external_library(path):
    for lib_filter in lgpl_libraries + not_lgpl_libraries:
        if lib_filter.match(path):
            lib_filter.triggered = True
            return True

    return False


def check_for_unused_library_matchers():
    """Fails the build if any library matchers have gone unused."""
    all_filters = lgpl_libraries + not_lgpl_libraries + banned_libraries

    if not all([f.triggered for f in all_filters]):
        print("WARNING: Some library filters went unused! This suggests that "
              "the filter is either malfunctioning or unnecessary. Please "
              "fix or remove the filter. Unused filters include:")

        for lib_filter in all_filters:
            if not lib_filter.triggered:
                print(f"    {lib_filter}")

        print("WARNING: Some library filters were unused")
