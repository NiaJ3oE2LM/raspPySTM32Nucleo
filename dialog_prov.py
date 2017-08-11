import dialog

d = dialog.Dialog(autowidgetsize=True)

code, tag = d.menu(title='RASPINUCLEO',
       text='info text under title',
       choices=[('1', 'c1'),('2', 'c2'),('2', 'c3')])

d.msgbox("you chose: {}".format(tag))
d.infobox(title='ciao',text="infobox")