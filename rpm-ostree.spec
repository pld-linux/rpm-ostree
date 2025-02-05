#
# Conditional build:
%bcond_without	apidocs		# API documentation
#
Summary:	Hybrid package/OSTree system
Summary(pl.UTF-8):	Hybrydowy system pakietów/OSTree
Name:		rpm-ostree
Version:	2024.8
Release:	2
License:	GPL v2+, LGPL v2+, Apache v2.0 or MIT
Group:		Applications/System
#Source0Download: https://github.com/coreos/rpm-ostree/releases
Source0:	https://github.com/coreos/rpm-ostree/releases/download/v%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	5ab400cf236d93f88afaeb9f49e8f41c
Patch0:		libdnf-gpgme-pkgconfig.patch
Patch1:		%{name}-types.patch
URL:		https://github.com/coreos/rpm-ostree
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.11
BuildRequires:	cargo
BuildRequires:	curl-devel
BuildRequires:	glib2-devel >= 1:2.50.0
BuildRequires:	gobject-introspection-devel >= 1.34.0
BuildRequires:	gtk-doc >= 1.15
BuildRequires:	json-glib-devel
BuildRequires:	libarchive-devel >= 3.3.3
BuildRequires:	libstdc++-devel >= 6:4.7
BuildRequires:	libtool >= 2:2.2.4
BuildRequires:	libxslt-progs
BuildRequires:	openssl-devel
BuildRequires:	ostree-devel >= 2023.7
BuildRequires:	pkgconfig
BuildRequires:	polkit-devel
BuildRequires:	rpm-build >= 4.6
# TODO: new features with 4.18.0+
BuildRequires:	rpm-devel >= 1:4.17
BuildRequires:	rust
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zchunk-devel >= 0.9.11
%if %{without system_libdnf}
# is system libdnf possible?
BuildRequires:	cmake >= 2.8.5
BuildRequires:	gpgme-devel
BuildRequires:	json-c-devel
BuildRequires:	libmodulemd-devel >= 2.11.2
BuildRequires:	librepo-devel >= 1.13.0
BuildRequires:	libsmartcols-devel
BuildRequires:	libsolv-devel >= 0.7.21
BuildRequires:	sqlite3-devel >= 3
BuildRequires:	zlib-devel
%endif
Requires:	%{name}-libs = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
rpm-ostree is a hybrid image/package system. It combines libostree as
a base image format, and accepts RPM on both the client and server
side, sharing code with the DNF project (specifically libdnf) and thus
bringing many of the benefits of both together.

%description -l pl.UTF-8
rpm-ostree to hybrydowy system obrazów/pakietów. Łączy libostree jako
podstawowy format obrazów i przyjmuje pakiety RPM zarówno po stronie
klienta, jak i serwera, współdzieląc kod z projektem DNF (w
szczególności libdnf), tym samym łącząc zalety obu rozwiązań.

%package -n bash-completion-rpm-ostree
Summary:	Bash completion for rpm-ostree commands
Summary(pl.UTF-8):	Bashowe dopełnianie parametrów poleceń rpm-ostree
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 1:2.0
BuildArch:	noarch

%description -n bash-completion-rpm-ostree
Bash completion for rpm-ostree commands.

%description -n bash-completion-rpm-ostree -l pl.UTF-8
Bashowe dopełnianie parametrów poleceń rpm-ostree.

%package libs
Summary:	Hybrid package/OSTree system library
Summary(pl.UTF-8):	Biblioteka hybrydowego systemu pakietów/OSTree
Group:		Libraries
Requires:	glib2 >= 1:2.50.0
Requires:	ostree >= 2023.7

%description libs
Hybrid package/OSTree system library.

%description libs -l pl.UTF-8
Biblioteka hybrydowego systemu pakietów/OSTree.

%package devel
Summary:	Header files for rpm-ostree library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki rpm-ostree
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	glib2-devel >= 1:2.50.0
Requires:	ostree-devel >= 2023.7

%description devel
Header files for rpm-ostree library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki rpm-ostree.

%package apidocs
Summary:	API documentation for rpm-ostree library
Summary(pl.UTF-8):	Dokumentacja API biblioteki rpm-ostree
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for rpm-ostree library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki rpm-ostree.

%prep
%setup -q
%patch -P 0 -p1 -d libdnf
%patch -P 1 -p1

# see autogen.sh
%{__sed} -e 's,$(libglnx_srcpath),'$(pwd)/libglnx,g < libglnx/Makefile-libglnx.am >libglnx/Makefile-libglnx.am.inc
ln -sf ../libglnx/libglnx.m4 buildutil/libglnx.m4

%ifarch x32
%{__sed} -i -e '/^cargo_build = / s/$/ --target x86_64-unknown-linux-gnux32/' Makefile-rpm-ostree.am
%{__sed} -i -e 's,^cargo_target_dir=,cargo_target_dir=x86_64-unknown-linux-gnux32/,' Makefile-rpm-ostree.am
%endif

%build
export PKG_CONFIG_ALLOW_CROSS=1
%{__gtkdocize}
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--enable-gtk-doc \
	--disable-silent-rules \
	--with-html-dir=%{_gtkdocdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
export PKG_CONFIG_ALLOW_CROSS=1

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	systemdunitdir=%{systemdunitdir}

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/librpmostree-1.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE
%attr(755,root,root) %{_bindir}/rpm-ostree
%attr(755,root,root) %{_libexecdir}/rpm-ostreed
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/rpm-ostreed.conf
%dir %{_libexecdir}/libostree/ext
%attr(755,root,root) %{_libexecdir}/libostree/ext/ostree-container
%attr(755,root,root) %{_libexecdir}/libostree/ext/ostree-ima-sign
%attr(755,root,root) %{_libexecdir}/libostree/ext/ostree-provisional-repair
%dir %{_libdir}/rpm-ostree
%{_libdir}/rpm-ostree/rpm-ostree-0-integration.conf
%{_libdir}/rpm-ostree/rpm-ostree-0-integration-opt-usrlocal.conf
%{_libdir}/rpm-ostree/rpm-ostree-0-integration-opt-usrlocal-compat.conf
%{_datadir}/dbus-1/interfaces/org.projectatomic.rpmostree1.xml
%{_datadir}/dbus-1/system-services/org.projectatomic.rpmostree1.service
%{_datadir}/dbus-1/system.d/org.projectatomic.rpmostree1.conf
%{_datadir}/polkit-1/actions/org.projectatomic.rpmostree1.policy
%{systemdunitdir}/rpm-ostree-bootstatus.service
%{systemdunitdir}/rpm-ostree-countme.service
%{systemdunitdir}/rpm-ostree-countme.timer
%{systemdunitdir}/rpm-ostree-fix-shadow-mode.service
%{systemdunitdir}/rpm-ostreed-automatic.service
%{systemdunitdir}/rpm-ostreed-automatic.timer
%{systemdunitdir}/rpm-ostreed.service
%{_mandir}/man1/rpm-ostree.1*
%{_mandir}/man5/rpm-ostreed.conf.5*
%{_mandir}/man8/rpm-ostree-countme.service.8*
%{_mandir}/man8/rpm-ostree-countme.timer.8*
%{_mandir}/man8/rpm-ostreed-automatic.service.8*
%{_mandir}/man8/rpm-ostreed-automatic.timer.8*

%files -n bash-completion-rpm-ostree
%defattr(644,root,root,755)
%{bash_compdir}/rpm-ostree

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/librpmostree-1.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/librpmostree-1.so.1
%{_libdir}/girepository-1.0/RpmOstree-1.0.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/librpmostree-1.so
%{_includedir}/rpm-ostree-1
%{_datadir}/gir-1.0/RpmOstree-1.0.gir
%{_pkgconfigdir}/rpm-ostree-1.pc

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/rpmostree
%endif
