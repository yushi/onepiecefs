DEST=/opt/opfs/bin
install:
	mkdir -p $(DEST)
	install -m755 executer $(DEST)/opfsd
	install -m755 executer $(DEST)/opfsmount
	install -m755 opfsd_reload.sh $(DEST)
	install -m644 opfsmount.py $(DEST)
	install -m644 opfsd.py $(DEST)
	install -m644 opfsc.py $(DEST)
	install -m644 opfsutil.py $(DEST)

package_osx:
	tar jcf opfs_`date +%Y%m%d%H%M`.tar.bz2 /opt/opfs
