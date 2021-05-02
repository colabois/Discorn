sed -i 's/class Ui_Guild(object):/class Ui_Guild(QWidget):/g' $@
sed -i '18,20d' $@