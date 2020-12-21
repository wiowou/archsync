# Maintainer: ActiveState Software Inc.
# Contributor: Mikhail f. Shiryaev <mr<dot>felixoid<at>gmail<dot>com>
pkgbase=komodo-pydbgp
# pkgname=(python-pydbgp python2-pydbgp)
pkgname=(python-pydbgp)
_srcrel=91033
_srcver=11.1.0
pkgver=11.1.0.${_srcrel}
pkgrel=1
pkgdesc="The Komodo IDE Python Remote Debugging component"
arch=('x86_64')
url="http://code.activestate.com/komodo/remotedebugging/"
license=('MIT')
depends=()
source=("http://downloads.activestate.com/Komodo/releases/${_srcver}/remotedebugging/Komodo-PythonRemoteDebugging-${_srcver}-${_srcrel}-linux-${arch[*]}.tar.gz")
md5sums=('09756df44b52d6d1e31d0ad0caa6d44a')

build() {
	cd "$srcdir/Komodo-PythonRemoteDebugging-${_srcver}-${_srcrel}-linux-${arch[*]}"
	cp pydbgpproxy py3_dbgpproxy
	sed -i '1s:/usr/bin/env python:/usr/bin/env python2:' pydbgp
	sed -i '1s:/usr/bin/env python:/usr/bin/env python2:' pydbgpproxy
    sed -i 's/ async/ is_async/g' python3lib/dbgp/client.py
    sed -i 's/(async/(is_async/g' python3lib/dbgp/client.py
    sed -i 's/ async/ is_async/g' pythonlib/dbgp/client.py
    sed -i 's/(async/(is_async/g' pythonlib/dbgp/client.py
}

package_python-pydbgp() {
	depends=(python)
	cd "$srcdir/Komodo-PythonRemoteDebugging-${_srcver}-${_srcrel}-linux-${arch[*]}"
	mkdir -p "${pkgdir}/usr/bin/"
	cp py3_dbgp "${pkgdir}/usr/bin/"
	cp py3_dbgpproxy "${pkgdir}/usr/bin/"
	cp -r python3lib/dbgp  "${pkgdir}/usr/bin"
}

# package_python2-pydbgp() {
# 	depends=(python2)
# 	cd "$srcdir/Komodo-PythonRemoteDebugging-${_srcver}-${_srcrel}-linux-${arch[*]}"
# 	mkdir -p "${pkgdir}/usr/bin/" 
# 	cp pydbgp "${pkgdir}/usr/bin/"
# 	cp pydbgpproxy "${pkgdir}/usr/bin/"
# 	cp -r pythonlib/dbgp2  "${pkgdir}/usr/bin"
# }
