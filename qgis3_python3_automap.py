import os

# set path of repo to working dir
#os.chdir("{{HOME}}/repos/qgis-autoprint-map")

print(env_vars);
project = QgsProject.instance()

layout = QgsPrintLayout(project)
layout.initializeDefaults()

pages = layout.pageCollection()
pages.beginPageSizeChange()
page = pages.page(0)
# Sets the page size to a known page and orientation
page.setPageSize('A4',  QgsLayoutItemPage.Landscape)
pages.endPageSizeChange()
page_center = page.pageSize().width() / 2
print("print page size width in mm: " + str(page.pageSize().width()))
print("print page size height in mm: " + str(page.pageSize().height()))

accessibility_uri = "file://" + os.getcwd() + "/input/bamako_accessibility_schools.csv?delimiter={}&crs=epsg:4326&wktField={}".format(",", "geometry")

road_uri = os.getcwd() + "/input/OSM_Roads/OSM_Roads.shp"
school_uri = os.getcwd() + "/input/osm_infrastructure/osm_schools.shp"

accessibility_style_uri = os.getcwd() + "/input/accessibility_style.qml"
road_style_uri = os.getcwd() + "/input/road_style.qml"
school_style_uri = os.getcwd() + "/input/school_style.qml"

# adding layers
accessibility_layer = QgsVectorLayer(accessibility_uri, "Accessibility Layer", "delimitedtext")

project.addMapLayer(accessibility_layer)

road_layer = QgsVectorLayer(road_uri,"Road Layer", "ogr")

project.addMapLayer(road_layer)

school_layer = QgsVectorLayer(school_uri,"OSM Schools", "ogr")

project.addMapLayer(school_layer)

# add styles
accessibility_layer.loadNamedStyle(accessibility_style_uri)

road_layer.loadNamedStyle(road_style_uri)

school_layer.loadNamedStyle(school_style_uri)

pdf_path = os.getcwd() + "/output/test.pdf"

#get margins and paper size right
lm = 50         # left margin
tm = 25         # upper margin
bm = 30         # lower margin

# paperSize = 'A4'
longSide = 297
shortSide = 210

x, y = lm, tm
w, h = longSide -  2 * lm, shortSide - bm

# Instantiate the map object
map = QgsLayoutItemMap(layout)

map.updateBoundingRect()
map.setRect(QRectF(x, y, w, h)) 
map.setPos(x,y)
map.setFrameEnabled(True)

extent2 = road_layer.extent()
xmin = extent2.xMinimum()
xmax = extent2.xMaximum()
ymin = extent2.yMinimum()
ymax = extent2.yMaximum()
#coords = [xmin, xmax, ymin, ymax]

new_extent = QgsRectangle(xmin-.05, ymin-.05, xmax+.05, ymax+.05)

map.setExtent(new_extent)

map.attemptSetSceneRect(QRectF(x, y, w, h))

layout.addItem(map)

title = QgsLayoutItemLabel(layout)
title.setText('Bamako Accessibility Map')
title.setFont(QFont('Arial', 36))
title.adjustSizeToText()
#title.setReferencePoint(QgsLayoutItem.UpperMiddle)
#title.attemptMove(QgsLayoutPoint(page_center, 10))
title.setPos(lm,5)
layout.addItem(title)

# legend does not display map unit symbology in print layout: https://issues.qgis.org/issues/19282
# as workaround using pixels instead

lyrs_to_add = [l for l in QgsProject().instance().layerTreeRoot().children() if l.isVisible()]
legend = QgsLayoutItemLegend(layout)


legend.setReferencePoint(QgsLayoutItem.LowerRight)

legend.setTitle('Legend')
legend.setAutoUpdateModel(False)
group = legend.model().rootGroup()
group.clear()

for l in lyrs_to_add:
    if l.nodeType() == 0:
        subgroup = group.addGroup(l.name())
        checked = l.checkedLayers()
        for c in checked:
            subgroup.addLayer(c)
    elif l.nodeType() == 1:
        group.addLayer(l.layer())

layout.addItem(legend)
legend.adjustBoxSize()
legend.setFrameEnabled(True)
legend.attemptMove(QgsLayoutPoint(10, 110, QgsUnitTypes.LayoutMillimeters))
legend.refresh()


subtitle = QgsLayoutItemLabel(layout)
subtitle.setText("Subtitle Here")
subtitle.setFont(QFont("Arial", 17))
subtitle.adjustSizeToText()
layout.addLayoutItem(subtitle)
subtitle.setPos(lm, 17)
#subtitle.attemptMove(QgsLayoutPoint(11, 20, QgsUnitTypes.LayoutMillimeters))   #allows moving text box


exporter = QgsLayoutExporter(layout)
exporter.exportToPdf(
    pdf_path, QgsLayoutExporter.PdfExportSettings())

# for some reason I am only able to get the height after the layout is exported
print("print legend height2 " + str(legend.sizeWithUnits().height()))
