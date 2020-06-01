#  -*- coding: utf-8 -*-
import gdspy
import matplotlib

def libinfo(lib):
    print('Library info:')
    print('  lib',lib)
    # print(dir(lib))
    print('  lib.name',lib.name)
    print('  lib.precision',lib.precision)
    print('  lib.unit',lib.unit)
    print('  len(lib.cells)',len(lib.cells))
def cellinfo(lib):
    print('Top cells info:')
    for cell in lib.top_level():
        print(' ',cell)
        print('     name',cell.name)
        print('     area',cell.area())
        d = cell.area(by_spec=True)
        for k in d:
            print('       layer',k,'area',d[k])
        for s in ['get_bounding_box', 'get_datatypes', 'get_dependencies', 'get_labels', 'get_layers', 'get_svg_classes']:
            print('    ',s,getattr(cell,s)())
        for s in ['get_paths', 'get_polygons', 'get_polygonsets']:
            print('    ',s,len(getattr(cell,s)()))
def getallpolygons(cell=None,layers=None,bounds=None,datatype=0): # returns list of (nx2 polygon array, polygon layer) tuples
    cell = cell if cell is not None else lib.top_level()[0]
    layers = layers if layers is not None else cell.get_layers()
    d = cell.get_polygons(by_spec=True)
    polygons = [(p,l) for l in layers for p in d[(l,datatype)]]
    # print(len(polygons),'polygons') # print(dir(polygons[0])) # print(polygons[0][:3])
    ds = [p.get_polygons(by_spec=True) for p in cell.get_paths()]
    pathpolys = [(p,l) for d in ds for l,dt in d for p in d[(l,dt)] if l in layers and dt==datatype]
    # print(len(pathpolys),'path polygons') # print(dir(pathpolys[0])) # print(pathpolys[0])
    return [(xy,l) for xy,l in polygons+pathpolys if inbounds(xy,bounds=bounds)]
def inbounds(xy,bounds): # xmin,xmax,ymin,ymax = bounds
    xs,ys = zip(*xy)
    x0,x1,y0,y1 = min(xs),max(xs),min(ys),max(ys)
    def boundingboxoverlap(bbi,bbj):
        if bbi is None or bbj is None: return True
        il,ir,ib,it = bbi # left,right,bottom,top
        jl,jr,jb,jt = bbj
        overlap = not (jl>ir or jr<il or jt<ib or jb>it) # https://gamedev.stackexchange.com/a/913
        return overlap
    return boundingboxoverlap((x0,x1,y0,y1),bounds)
def plotpolylist(polylist,**plotargs):
    layers = [l for (xy,l) in polylist]
    labels = []
    for layer in layers:
        labels += [layer] if layer not in labels else ['']
    xs = [xy[:,0] for (xy,l) in polylist]
    ys = [xy[:,1] for (xy,l) in polylist]
    d = {l:n for n,l in enumerate(set(layers))}
    cs = ['C'+str(d[l]) for l in layers]
    import matplotlib.pyplot as plt
    for wx,wy,c,s in zip(xs,ys,cs,labels):
        plt.plot(list(wx)+[wx[0]], list(wy)+[wy[0]], c, label=s)
    plt.legend(); plt.xlabel('x (µm)'); plt.ylabel('y (µm)')
    plt.show()
def info(file):
    lib = gdspy.GdsLibrary(infile=file,units='import')
    libinfo(lib)
    cellinfo(lib)
def plot(file,layers=None,bounds=None,**plotargs):
    lib = gdspy.GdsLibrary(infile=file,units='import') # https://gdspy.readthedocs.io/en/stable/reference.html#gdspy.GdsLibrary
    # cell = lib.top_level()[0]
    # polylist = getallpolygons(cell,layers,bounds)
    polylist = [p for cell in lib.top_level() for p in getallpolygons(cell,layers,bounds)]
    plotpolylist(polylist,**plotargs)

if __name__ == '__main__':
    import sys
    files = sys.argv[1:]
    # files = ['photonics.gds']
    for file in files:
        info(file)
        plot(file)