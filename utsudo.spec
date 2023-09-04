ExcludeArch: i686

Summary: The tudo respect sudo
Name: utsudo
Version: 0.0.1
Release: 0%{?dist}
License: ISC
Group: Applications/System
URL: https://www.sudo.ws/

Source0: %{name}-%{version}.tar.gz
Source1: utsudoers
Source2: utsudo-ldap.conf
Source3: utsudo.conf

Requires: /etc/pam.d/system-auth
Requires: /usr/bin/vi
Requires(post): /bin/chmod
Requires: sudo

BuildRequires: /usr/sbin/sendmail
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: bison
BuildRequires: flex
BuildRequires: gettext
BuildRequires: groff
BuildRequires: libtool
BuildRequires: audit-libs-devel
BuildRequires: libcap-devel
BuildRequires: libgcrypt-devel
BuildRequires: libselinux-devel
BuildRequires: openldap-devel
BuildRequires: pam-devel
BuildRequires: zlib-devel
BuildRequires: cargo
BuildRequires: rust
BuildRequires: patchelf

%description
Sudo (superuser do) allows a system administrator to give certain
users (or groups of users) the ability to run some (or all) commands
as root while logging all commands and arguments. Sudo operates on a
per-command basis.  It is not a replacement for the shell.  Features
include: the ability to restrict what commands a user may run on a
per-host basis, copious logging of each command (providing a clear
audit trail of who did what), a configurable timeout of the sudo
command, and the ability to use the same configuration file (sudoers)
on many different machines.

%prep
%setup -q

%build
# Remove bundled copy of zlib
rm -rf zlib/
autoreconf -I m4 -fv --install

%ifarch s390 s390x sparc64
F_PIE=-fPIE
%else
F_PIE=-fpie
%endif

export CFLAGS="$RPM_OPT_FLAGS $F_PIE" LDFLAGS="-pie -Wl,-z,relro -Wl,-z,now"

%configure \
        --prefix=%{_prefix} \
        --sbindir=%{_sbindir} \
        --libdir=%{_libdir} \
        --docdir=%{_pkgdocdir} \
        --disable-root-mailer \
        --with-logging=syslog \
        --with-logfac=authpriv \
        --with-pam \
        --with-pam-login \
        --with-editor=/bin/vi \
        --with-env-editor \
        --with-ignore-dot \
        --with-tty-tickets \
        --with-ldap \
        --with-ldap-conf-file="%{_sysconfdir}/utsudo-ldap.conf" \
        --with-selinux \
        --with-passprompt="[utsudo] password for %p: " \
        --with-linux-audit \
        --with-sssd
make

%check
## make check

%install
rm -rf $RPM_BUILD_ROOT


# Update README.LDAP (#736653)
sed -i 's|/etc/ldap\.conf|%{_sysconfdir}/utsudo-ldap.conf|g' README.LDAP

make install DESTDIR="$RPM_BUILD_ROOT" install_uid=`id -u` install_gid=`id -g` sudoers_uid=`id -u` sudoers_gid=`id -g`
install -p -d -m 700 $RPM_BUILD_ROOT/var/db/sudo
install -p -d -m 700 $RPM_BUILD_ROOT/var/db/sudo/lectured
install -p -d -m 750 $RPM_BUILD_ROOT/etc/utsudoers.d
install -p -c -m 0440 %{SOURCE1} $RPM_BUILD_ROOT/etc/utsudoers
install -p -c -m 0640 %{SOURCE3} $RPM_BUILD_ROOT/etc/utsudo.conf
install -p -c -m 0640 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/utsudo-ldap.conf

# Add sudo to protected packages
install -p -d -m 755 $RPM_BUILD_ROOT/etc/dnf/protected.d/
touch utsudo.conf
echo utsudo > utsudo.conf
install -p -c -m 0644 utsudo.conf $RPM_BUILD_ROOT/etc/dnf/protected.d/
rm -f utsudo.conf
rm -f $RPM_BUILD_ROOT%{_bindir}/cvtsudoers
rm -f $RPM_BUILD_ROOT%{_bindir}/sudoreplay
rm -f $RPM_BUILD_ROOT%{_sbindir}/visudo
rm -f $RPM_BUILD_ROOT/etc/sudoers

chmod +x $RPM_BUILD_ROOT%{_libexecdir}/utsudo/*.so # for stripping, reset in %%files

# Don't package LICENSE as a doc
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/LICENSE

# Remove examples; Examples can be found in man pages too.
rm -rf $RPM_BUILD_ROOT%{_datadir}/examples/sudo

# Remove all .la files
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

# Remove sudoers.dist
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/sudoers.dist

# Remove sudo_plugin.h -add by uos
rm -f $RPM_BUILD_ROOT%{_includedir}/sudo_plugin.h

%find_lang utsudo
%find_lang utsudoers

cat utsudo.lang utsudoers.lang > utsudo_all.lang
rm utsudo.lang utsudoers.lang

mkdir -p $RPM_BUILD_ROOT/etc/pam.d
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/utsudo

%clean
rm -rf $RPM_BUILD_ROOT

%files -f utsudo_all.lang
%defattr(-,root,root)
%attr(0440,root,root) %config(noreplace) /etc/utsudoers
%attr(0640,root,root) %config(noreplace) /etc/utsudo.conf
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/utsudo-ldap.conf
%attr(0750,root,root) %dir /etc/utsudoers.d/
%attr(0644,root,root) %{_tmpfilesdir}/utsudo.conf
%attr(0644,root,root) /etc/dnf/protected.d/utsudo.conf
%dir /var/db/sudo
%dir /var/db/sudo/lectured
%attr(4111,root,root) %{_bindir}/utsudo
%{_bindir}/utsudoedit
%dir %{_libexecdir}/utsudo
%attr(0755,root,root) %{_libexecdir}/utsudo/sesh
%attr(0644,root,root) %{_libexecdir}/utsudo/sudo_noexec.so
%attr(0644,root,root) %{_libexecdir}/utsudo/sudoers.so
%attr(0644,root,root) %{_libexecdir}/utsudo/group_file.so
%attr(0644,root,root) %{_libexecdir}/utsudo/system_group.so
%{_libexecdir}/utsudo/libutsudo_util.so
%{_libexecdir}/utsudo/libutsudo_util.so.?
%attr(0644,root,root) %{_libexecdir}/utsudo/libutsudo_util.so.?.?.?
%dir %{_pkgdocdir}/
%{!?_licensedir:%global license %%doc}
%license doc/LICENSE

# Make sure permissions are ok even if we're updating
%post
/bin/chmod 0440 /etc/utsudoers || :

%changelog
* Wed May 10 2022 Lujun <wanglujun@uniontech.com> - 0.0.1
- init.
