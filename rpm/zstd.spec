%ifarch %{ix86} x86_64
%bcond_without pzstd
%else
# aarch64 and armv7hl at least currently segfault
# in ThreadPool test for the pzstd util
%bcond_with pzstd
%endif

# Disable tests as they require bigger workers and take quite a bit time
%bcond_with tests

Name:           zstd
Version:        1.5.0
Release:        1
Summary:        Zstd compression library

License:        BSD and GPLv2
URL:            https://github.com/facebook/zstd
Source0:        https://github.com/facebook/zstd/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Patch0:         0001-Use-r-for-extended-regex-instead-of-E-as-our-sed-is-.patch

BuildRequires: make
BuildRequires:  gcc gtest-devel
%if %{with pzstd}
BuildRequires:  gcc-c++
%endif

%description
Zstd, short for Zstandard, is a fast lossless compression algorithm,
targeting real-time compression scenarios at zlib-level compression ratio.

%package -n lib%{name}
Summary:        Zstd shared library

%description -n lib%{name}
Zstandard compression shared library.

%package -n lib%{name}-devel
Summary:        Header files for Zstd library
Requires:       lib%{name}%{?_isa} = %{version}-%{release}

%package -n lib%{name}-static
Summary:        Static variant of the Zstd library
Requires:       lib%{name}-devel = %{version}-%{release}

%description -n lib%{name}-devel
Header files for Zstd library.

%description -n lib%{name}-static
Static variant of the Zstd library.

%prep
%autosetup -n %{name}-%{version}/%{name} -p1
find -name .gitignore -delete

%build
export CFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"
%make_build -C lib lib-mt
%make_build -C programs
%if %{with pzstd}
export CXXFLAGS="$RPM_OPT_FLAGS"
%make_build -C contrib/pzstd
%endif

%check
export CFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"
%if %{with test}
make -C tests test-zstd
%endif
%if %{with pzstd}
export CXXFLAGS="$RPM_OPT_FLAGS"
%if %{with test}
make -C contrib/pzstd test
%endif
%endif

%install
make DESTDIR=%{buildroot} INSTALL_ROOT=%{buildroot} PREFIX=%{_prefix} LIBDIR=%{_libdir} install
%if %{with pzstd}
install -D -m755 contrib/pzstd/pzstd %{buildroot}%{_bindir}/pzstd
%endif

# We don't need the man pages
rm -rf  %{buildroot}%{_mandir}

%post -n lib%{name} -p /sbin/ldconfig
%postun -n lib%{name} -p /sbin/ldconfig

%files
%doc CHANGELOG README.md
%{_bindir}/%{name}
%if %{with pzstd}
%{_bindir}/p%{name}
%endif
%{_bindir}/%{name}mt
%{_bindir}/un%{name}
%{_bindir}/%{name}cat
%{_bindir}/%{name}grep
%{_bindir}/%{name}less
%license COPYING LICENSE

%files -n lib%{name}
%{_libdir}/libzstd.so.*
%license COPYING LICENSE

%files -n lib%{name}-devel
%{_includedir}/zdict.h
%{_includedir}/zstd.h
%{_includedir}/zstd_errors.h
%{_libdir}/pkgconfig/libzstd.pc
%{_libdir}/libzstd.so

%files -n lib%{name}-static
%{_libdir}/libzstd.a
