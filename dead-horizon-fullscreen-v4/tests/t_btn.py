import sys; sys.path.insert(0,'/home/claude')
from h import *
url=sys.argv[1]
with sync_playwright() as p:
    for (w,h) in [(1280,720),(1920,1080)]:
        b,ctx,pg=launch(p,w,h); start(pg,url)
        r=pg.evaluate("""()=>{const a=document.getElementById('fullscreen-toggle').getBoundingClientRect(),e=document.getElementById('exitFS').getBoundingClientRect(),m=document.getElementById('metaBtn').getBoundingClientRect();return{fs:[a.left,a.right],exit:[e.left,e.right],meta:[m.left,m.right],overlap_fs_exit:a.right-e.left,gap_meta_fs:a.left-m.right}}""")
        print(w,r); b.close()
