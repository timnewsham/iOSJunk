#!/usr/bin/env python
"""
Read out the iMessage attachments from a MobileSync backup (iTunes).
The backup must be unencrypted.
Warning: Output files will go into the current directory!
"""

import sys, os, hashlib, sqlite3, time, shutil

# XXX hardwired for now -- this should be the udid name for your device
udid = '14d74a7f5981f909303e6cc834c2ae6e84d8fd8b'

def syncDir(udid) :
    """Get mobile sync dir"""
    home = os.environ['HOME']
    # XXX this is the osx path.. will be diff in windows
    return '%s/Library/Application Support/MobileSync/Backup/%s' % (home, udid)

def utime(itime) :
    """Convert iOS time to unix time"""
    return itime + 978307222 # unix epoch is 1970, ios is 2001

def syncFile(udid, fn) :
    h = hashlib.sha1(fn).hexdigest()
    return os.path.join(syncDir(udid), h[:2], h)

def getMessageDb(udid) :
    fn = syncFile(udid, 'HomeDomain-Library/SMS/sms.db')
    return sqlite3.connect(fn)

def uniqFn(files, fn) :
    if fn not in files :
        return fn

    if '.' in fn :
        ext = fn.split('.')[-1]
        base = fn[: -(len(ext) + 1)]
    else :
        ext = None
        base = fn
    for n in xrange(1, 10000) :
        fn2 = '%s_%d' % (base, n)
        if ext is not None :
            fn2 += '.' + ext
        if fn2 not in files :
            #print 'uniq', fn2
            return fn2
    raise Exception("Cant deduplicate %s" % fn)

def replacePrefix(fn, pref, pref2) :
    if fn.startswith(pref) :
        return pref2 + fn[len(pref):]
    return fn

def mediaFile(udid, fn) :
    fn = replacePrefix(fn, '~/Library', 'MediaDomain-Library')
    return syncFile(udid, fn)

def getAttachments(udid) :
    files = set()
    c = getMessageDb(udid).cursor()
    for it,fn,xfn in c.execute('SELECT created_date,filename,transfer_name from attachment') :
        ut = utime(it)
        tfn = uniqFn(files, os.path.basename(xfn))
        files.add(tfn)
        hfn = mediaFile(udid, fn)
        #print time.ctime(ut), tfn, fn, xfn
        if os.path.exists(hfn) :
            shutil.copyfile(hfn, tfn)
            os.utime(tfn, (ut,ut))
        else :
            # XXX other domains?
            # ie: /private/var/tmp/com.apple.MobileSMS/Media/D10F3A7D-EC22-4F06-A3C9-DF2199C48691/Audio Message.amr
            print 'cant find %s - %s' % (fn, hfn)
   
getAttachments(udid)

