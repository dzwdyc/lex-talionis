import os
# Terrain Data Menu
from PyQt4 import QtGui, QtCore

import Code.Engine as Engine
# So that the code basically starts looking in the parent directory
Engine.engine_constants['home'] = '../'

from DataImport import Data
from CustomGUI import SignalList

class Autotiles(object):
    def __init__(self):
        self.autotiles = []
        self.autotile_frame = 0

    def load(self, auto_loc):
        # Auto-tiles
        self.autotile_frame = 0
        if os.path.exists(auto_loc):
            files = sorted([fp for fp in os.listdir(auto_loc) if fp.startswith('autotile') and fp.endswith('.png')], key=lambda x: int(x[8:-4]))
            self.autotiles = [QtGui.QImage(auto_loc + image) for image in files]
        else:
            self.autotiles = []

    def update(self, current_time):
        time = 483  # 29 ticks
        mod_time = current_time%(len(self.autotiles)*time)
        self.autotile_frame = mod_time/time

    def draw(self):
        if self.autotiles:
            return self.autotiles[self.autotile_frame]
        else:
            return None

    def __nonzero__(self):
        return bool(self.autotiles)

class TileData(object):
    def __init__(self):
        self.tiles = {}

    def clear(self):
        self.tiles = {}

    def get_tile_data(self):
        return self.tiles

    def load(self, tilefp):
        self.tiles = {}
        tiledata = QtGui.QImage(tilefp)
        colorkey, self.width, self.height = self.build_color_key(tiledata)
        self.populate_tiles(colorkey)

    def build_color_key(self, tiledata):
        width = tiledata.width()
        height = tiledata.height()
        mapObj = [] # Array of map data
    
        # Convert to a mapObj
        for x in range(width):
            mapObj.append([])
        for y in range(height):
            for x in range(width):
                pos = QtCore.QPoint(x, y)
                color = QtGui.QColor.fromRgb(tiledata.pixel(pos))
                mapObj[x].append((color.red(), color.green(), color.blue()))

        return mapObj, width, height

    def populate_tiles(self, colorKeyObj):
        for x in range(len(colorKeyObj)):
            for y in range(len(colorKeyObj[x])):
                cur = colorKeyObj[x][y]
                self.tiles[(x, y)] = cur

class TerrainMenu(QtGui.QWidget):
    def __init__(self, terrain_data, view, window=None):
        super(TerrainMenu, self).__init__(window)
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.window = window

        self.view = view

        self.list = SignalList(self)
        self.list.setMinimumSize(128, 320)
        self.list.uniformItemSizes = True
        self.list.setIconSize(QtCore.QSize(32, 32))

        # Ingest terrain_data
        for color, terrain in Data.terrain_data.iteritems():
            tid, name = terrain
            pixmap = QtGui.QPixmap(32, 32)
            pixmap.fill(QtGui.QColor(color[0], color[1], color[2]))

            item = QtGui.QListWidgetItem(tid + ': ' + name)
            item.setIcon(QtGui.QIcon(pixmap))
            self.list.addItem(item)

        self.grid.addWidget(self.list, 0, 0)

    def get_current_color(self):
        color = Data.terrain_data.keys()[self.list.currentRow()]
        print(color)
        return color

    def set_current_color(self, color):
        idx = Data.terrain_data.keys().index(color)
        self.list.setCurrentRow(idx)

    def get_info(self, color):
        return Data.terrain_data[color]

    def get_info_str(self, color):
        tid, name = Data.terrain_data[color]
        return str(tid) + " - " + str(name)

    # def trigger(self):
    #     self.view.tool = 'Terrain'
