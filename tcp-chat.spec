Name:           tcp-chat
Version:        1.0
Release:        1%{?dist}
Summary:        Simple TCP chat

License:        MIT
BuildArch:      noarch
Requires:       python3

%description
Simple TCP chat for YADRO test task

%prep
cp -r %{_sourcedir}/chat .

%build
# skip

%install
mkdir -p %{buildroot}/opt/tcp-chat
cp -r chat/* %{buildroot}/opt/tcp-chat/
mkdir -p %{buildroot}/usr/bin
cp chat/startup/tcp-server %{buildroot}/usr/bin/tcp-server
cp chat/startup/tcp-client %{buildroot}/usr/bin/tcp-client

%files
/opt/tcp-chat
/usr/bin/tcp-server
/usr/bin/tcp-client

%changelog
* Sun May 04 2025 Yarik - 1.0-1
- Test