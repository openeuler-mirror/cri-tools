%global goipath         github.com/kubernetes-sigs/cri-tools
%define gobuild(o:) %{expand:
  # https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
  %global _dwz_low_mem_die_limit 0
  %ifnarch ppc64
  go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-}%{?currentgoldflags} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}' -compressdwarf=false" -a -v -x %{?**};
  %else
  go build                -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-}%{?currentgoldflags} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}' -compressdwarf=false" -a -v -x %{?**};
  %endif
}
%bcond_with check
%global built_tag v%{version}

Name:          cri-tools
Version:       1.22.0
Release:       1
Summary:       CLI and validation tools for Container Runtime Interface
License:       ASL 2.0
URL:           https://%{goipath}
Source0:       %url/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:       https://github.com/cpuguy83/go-md2man/archive/v1.0.10.tar.gz
ExclusiveArch: %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm} ppc64le s390x}
BuildRequires: golang, glibc-static, git
Provides:      crictl = %{version}-%{release}

%description
%{summary}

%prep
%setup -q
tar -xf %SOURCE1

%build
GO_MD2MAN_PATH="$(pwd)%{_bindir}"
mkdir -p _build/bin $GO_MD2MAN_PATH
cd go-md2man-*
go build -mod=vendor -o ../_build/bin/go-md2man .
cp ../_build/bin/go-md2man $GO_MD2MAN_PATH/go-md2man
export PATH=$GO_MD2MAN_PATH:$PATH
cd -

%gobuild -o bin/crictl %{goipath}/cmd/crictl
go-md2man -in docs/crictl.md -out docs/crictl.1

%install
# install binaries
install -dp %{buildroot}%{_bindir}
install -p -m 755 ./bin/crictl %{buildroot}%{_bindir}

# install manpage
install -dp %{buildroot}%{_mandir}/man1
install -p -m 644 docs/crictl.1 %{buildroot}%{_mandir}/man1

%files
%license LICENSE
%doc CHANGELOG.md CONTRIBUTING.md OWNERS README.md RELEASE.md code-of-conduct.md
%doc docs/{benchmark.md,roadmap.md,validation.md}
%{_bindir}/crictl
%{_mandir}/man1/crictl*

%changelog
* Mon Mar 21 2022 fushanqing <fushanqing@kylinos.cn> - 1.22.0-1
- Init Package