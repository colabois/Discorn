sed -i 's/class Ui_Tab(object):/class Ui_Tab(QWidget):/g' $@
sed -i '18,20d' $@