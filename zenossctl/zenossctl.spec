#
# RPM spec file for Zenossctl
#
# Supported/tested build targets:
# - Fedora: 21, 20, 19, 18
# - RHEL: 7, 6, 5, 4
# - CentOS: 7, 6, 5
# - SLES: 12, 11sp3, 11sp2, 10
# - OpenSuSE: Factory, 13.1, 12.3, 12.2
#
# If it doesn't build on the Open Build Service (OBS) it's a bug.
# https://build.opensuse.org/project/subprojects/home:libertas-ict
#

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%global debug_package %{nil}
%define _binaries_in_noarch_packages_terminate_build 1
%define _unpackaged_files_terminate_build 1

%define name zenossctl
%define version 1.1.0
%define unmangled_version 1.1.0
%define release 1

Summary: Libraries and tools to manage device registration in Zenoss
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv2
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Vendor: Jorgen Maas <jorgen.maas@gmail.com>
Url: https://github.com/jmaas/zenossctl

%if %{?suse_version: %{suse_version} > 1110} %{!?suse_version:1}
BuildArchitectures: noarch
%endif

BuildRequires: python >= 2.3
Requires: python >= 2.3

%if 0%{?suse_version} == 1010
BuildRequires: python-devel
%endif


%description
zenossctl provides a library and tools to help with Zenoss object management.

The library is geared towards sysadmins and provides a workflow oriented and
pythonic interface to the Zenoss JSON API.

The commandline tool provides functions to deal with device registration,
deletion, groups management and stuff like that.

Project homepage: https://github.com/jmaas/zenossctl
Packages: http://download.opensuse.org/repositories/home:/libertas-ict:/
Documentation: http://zenossctl.readthedocs.org

%prep
%setup -n %{name}-%{unmangled_version}

%build
%{__python} setup.py build

%install
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=%{_prefix} --root=%{buildroot} --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%{python_sitelib}/*
%dir /etc/zenossctl
%config(noreplace) %attr(640,root,root) /etc/zenossctl/zenossctl.json
%doc README AUTHORS COPYING

%changelog
* Wed Apr 09 2014 Jörgen Maas <jorgen.maas@gmail.com>
- 1.0.0 - Initial release

# EOF
