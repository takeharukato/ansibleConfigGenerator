Name:           ansibleConfigGenerator
Version:        0.1.0
Release:        1%{?dist}
Summary:        genAnsibleConf command-line generators

License:        BSD
URL:            https://github.com/takeharukato/ansibleConfigGenerator
Source0:        ansibleconfiggenerator-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pyyaml
BuildRequires:  gettext
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  make
BuildRequires:  gcc

Requires:       python3 >= 3.9
Requires:       python3-pyyaml

%description
Generates host_vars, tfvars, and design-sheet artifacts from topology inputs.
Includes generator scripts and Python modules.

%prep
%autosetup -n ansibleconfiggenerator-%{version}

%build
./autogen.sh
%configure PYTHON=python3
%make_build

%install
rm -rf %{buildroot}
%make_install
install -D -m 0644 config/genAnsibleConf.system-config.yaml \
	%{buildroot}%{_sysconfdir}/genAnsibleConf/config.yaml
install -D -m 0644 config/genAnsibleConf.user-config.yaml \
	%{buildroot}%{_datadir}/genAnsibleConf/examples/genAnsibleConf.user-config.yaml

%files
%license LICENSE
%{_bindir}/generate_*.py
%{_bindir}/validate_hostvars_matrix.py
%dir /usr/lib/python*/site-packages/genAnsibleConf
/usr/lib/python*/site-packages/genAnsibleConf/*

%config(noreplace) %{_sysconfdir}/genAnsibleConf/config.yaml
%dir %{_datadir}/genAnsibleConf
%dir %{_datadir}/genAnsibleConf/schema
%{_datadir}/genAnsibleConf/schema/*.yaml
%dir %{_datadir}/genAnsibleConf/examples
%{_datadir}/genAnsibleConf/examples/*.yaml

# locale
%dir %{_datadir}/locale
%{_datadir}/locale/*/LC_MESSAGES/ansibleConfigGenerator.mo

%changelog
* Wed Feb 11 2026 Takeharu KATO <tkato1219@gmail.com> - 0.1.0-1
- Initial RPM package for ansibleConfigGenerator
