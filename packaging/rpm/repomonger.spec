Name:           repomonger
Version:        0.1
Release:        0
Summary:        A few python scripts for yum repo clone/copy/assemble
License:        GPLv3
URL:            https://github.com/weaselkeeper/repomonger
Group:          System Environment/Base
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       python
Requires:       rpm-python
Requires:       python-argparse
Requires:       python-simplejson

%description
A few utilities to clone, copy, assemble, and otherwise make available, yum
repos.

%prep
%setup -q -n %{name}

%install
rm -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/repomonger
#%{__mkdir_p} %{buildroot}%{_datadir}/repomonger/plugins
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/repomonger
#cp -r ./plugins/*.py %{buildroot}%{_datadir}/repomonger/plugins/
cp -r ./*.py %{buildroot}%{_bindir}/
cp -r ./config/* %{buildroot}%{_sysconfdir}/repomonger

%files
%{_bindir}/*.py
%{_sysconfdir}/repomonger/*
#%{_datadir}/repomonger/*

%pre

%post

%clean
rm -rf %{buildroot}

%changelog
* Sat Jul 27 2013 Jim Richardson <weaselkeeper@gmail.com> - 0.1
- Initial RPM build structure added.
