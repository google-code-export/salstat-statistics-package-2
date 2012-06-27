# referencias  http://www.daniweb.com/code/snippet216634.html#
# retorna un bitmap dado el nombre de la clase especifica
# se modificara
from cStringIO import StringIO
from base64 import b64decode, encodestring
from os.path import exists
from wx import BitmapFromImage, ImageFromStream, IconFromBitmap


class imageEmbed:
    def __init__(self):
        pass
    def __conversion__(self, data):
        jpg1 = b64decode(data)
        # convert jpg stream to a data stream
        stream1 = StringIO(jpg1)
        # convert to a bitmap
        return BitmapFromImage(ImageFromStream(stream1))
    
    def convertFromfile(self,pathFile, show = False):
        # muestra el string correspondiente para embeber una imagen en codigo
        #  dada la ruta
        if not exists(pathFile):
            raise StandardError('Ruta Inexistente: ' + str(pathFile))
        if show:
            print "   "
            print(pathFile.split('\\')[-1])
            jpg_text = 'jpg1_b64 = \\\n"""' + encodestring(open(pathFile,"rb").read()) + '"""'
            print jpg_text
        return jpg_text
    
    def disk(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAH+SURBVBgZBcE9i11VGAbQtc/sO0OCkqhg\nhEREAwpWAWUg8aMVf4KFaJEqQtAipTZWViKiCGOh2Ap2gmJhlSIWFsFOxUK0EsUM3pl79n4f12qH\nb3z3Fh7D83gC95GOJsDe0ixLk5Qq/+xv/Lw9Xd+78/HLX3Y8fXTr2nWapy4eCFKxG7Fby97SnDlY\ntMbxthyfzHO//nl85fNvfvnk8MbX5xa8IHx1518Vkrj54Q+qQms2vVmWZjdiu5ZR2rT01166/NCZ\ng/2PFjwSVMU6yjoC1oq+x6Y3VbHdlXWExPd379nf7Nmejv2Os6OC2O4KLK0RNn3RNCdr2Z5GJSpU\n4o+/TkhaJ30mEk5HwNuvX7Hpi76wzvjvtIwqVUSkyjqmpHS0mki8+9mPWmuWxqYvGkbFGCUAOH/+\nQevYI9GFSqmaHr5wkUYTAlGhqiRRiaqiNes6SOkwJwnQEqBRRRJEgkRLJGVdm6R0GLMQENE0Ekmk\nSkQSVVMqopyuIaUTs0J455VLAAAAAODW0U/GiKT0pTWziEj44PZ1AAAAcPPqkTmH3QiJrlEVDXDt\n0qsAAAAAapa5BqUnyaw0Am7//gUAAAB49tEXzTmtM5KkV/y2G/X4M5fPao03n/sUAAAAwIX7y5yB\nv9vhjW/fT/IkuSp5gJKElKRISYoUiSRIyD1tufs/IXxui20QsKIAAAAASUVORK5CYII=\n""")
    def pageexcel(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\nU29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAALDSURBVBgZBcFNiFVVAADg75x777z50Rmd\nDJG0phpTIwq1cqP9IBqlLaxNpYVSVIvahLVLCqFFoGEZQkQhgdGilUghaqRNIKgUZEmQlCBlmmOm\n772Zd+85fV/IOVuz7ejmgeHWxhgsRz8CCMiBnNQp/Xbln3w4XJ18/die9dMAIefssXcmjn326vIl\nMYZZmUIGIGfILl7r2Xfiir/OTbV//unM6Hd71k9BCbEIi/rKYtbpvxUxBAI50eSkrrNOr/HQwplW\n3FE6ni4O5rR48sFXDsz+dve6qQghhBk556KviKpIGSgiRSAEooBk3nCf9ffNMzbeGiiHhz6F8NSO\n1WdTHh2bNZhCk4Nl44+7fP2Sb37cK6NVzdCk2rplz9j0wEtaVandnbbpvZP1wbdXVSVOvfzI5ls7\nrT/9fvmMUyf3q1PbsoX3mG5q7XZHMmp8wdOOn6ulNG3VbS2hjDVEbPzw64PNDXnc8NCwRXfNU8ZB\nl65e1m53lcVcW9a8b3hoRH9fob+vkkVCBPHz1w5NtZsne19M7LVkYLWZ/QPGF92i2+mq69ILa3ca\nqFqqMuorCq0ySsgZiNBuHy6+//WIXQe2u3/OBk3ZceeSu031Jp3+45CyoCqCMgZlETWJJgHx3jdu\nevFa5+NqxeKVchXs3P+WRxc8a9Il88du99WJDzy/a0zIQRmDIgb9VdDUGURsI5s4fcQvZ3/QmW58\ncuQjT4w9Z2TmbKM3L7D01pUyUiajKqJ6ugbliXfPz3/4zYnOvq3L+y9eq8C/1y/4cmK7691JIUQj\ngzeqIlUMIOWsN5VACXXdaBoARobm2rJ2NwAAgJyyXrcGEeqplOqUMgAAAABAWcZUN6mGEnrd5sJQ\nXzFH6A3lnKNMAowMlCBnBqooBKkqwn9Nnc5DCSHkHWu3Ht0QQlia5UEAmYwsAxl0U0qnymgf/A8e\nWStYAg6kAQAAAABJRU5ErkJggg==\n""")
    def printer(self):
        return self.__conversion__(\
            """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0\n
            U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAJtSURBVDjLjZPfS1NhGMfPXfh3OG/E/yBI\n
            mNkqrYGCzAthh+WNgXihwQYb2CoYukGwsdRLoYUWQbRAhqzc2Q91IrrVhlhLqznL5Tyb23m3s317\n
            z1szBzM68Lk47/N9Pud5XjgcAK7OVfM7/a2piE87HalRoLVHStrp1VKvLVi7fE9wns/WaXi58Ugo\n
            H4kl/CxIyOZ/cyRKSKRFmF/tw/B4p3jl7utLFwp6baHiySnBxheZUkHkM8HKrgSpUsVGWsaDN/tQ\n
            G/1PLxT02EIlRbBJBZtfZaztlSF8JEgdFqBMdnh8im7LSqWpYHJysqXHFiS5AkGMfi12UP0zRRm+\n
            D6fwxvPI0dWu3Q8QvV7f0iCgzQZKnl4WjqkgcVDDeyrYpqLoXoWtsbxTpLUyrlsFDA4O5vv7+w1M\n
            QBu7Z2dnEY1GcXsqjCwVJDM1JCixb1Vs0VXCdIoAXSVLBTcfhhEIBDA+Pg6NRtOtCLbpg0wmA7PZ\n
            /F8oWUEQMDAwsKsIiCzLUFhfX4coiv8kFAqhnh8bG6txFosFhBDG4uIiUqkUEzVDqc3Pz5/leZ4H\n
            ZzKZkEgkGG63G8lkEn6/vylKxuFwnOU7OzvBTUxMwOfzMex2O+LxOJaWlpoSi8VgtVrP8u3t7eDo\n
            HvB6vQyXywV6Jwyj0YjR0VE2Zl9fH7q6uqBWq9lZPd/W1gZuZGSk6vF42IHSuPD8JZbfBpvybOEF\n
            Ojo6WHZubg6tra3gDAbDzNDQ0LZOpwPvCqNYIjg6IfhBOcxJSGdL2PtewKeMiKJUBu8MQ6VSKc1b\n
            FFPDv8C7ItXhJ2sYdv/lDmOVodR4Z6R6vucXuxIEyKz+W40AAAAASUVORK5CYII=\n
            """)
    def cancel(self):
        return self.__conversion__( \
            """iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0
            U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAHdSURBVDjLpZNraxpBFIb3a0ggISmmNISW
            XmOboKihxpgUNGWNSpvaS6RpKL3Ry//Mh1wgf6PElaCyzq67O09nVjdVlJbSDy8Lw77PmfecMwZg
            /I/GDw3DCo8HCkZl/RlgGA0e3Yfv7+DbAfLrW+SXOvLTG+SHV/gPbuMZRnsyIDL/OASziMxkkKkU
            QTJJsLaGn8/iHz6nd+8mQv87Ahg2H9Th/BxZqxEkEgSrq/iVCvLsDK9awtvfxb2zjD2ARID+lVVl
            babTgWYTv1rFL5fBUtHbbeTJCb3EQ3ovCnRC6xAgzJtOE+ztheYIEkqbFaS3vY2zuIj77AmtYYDu
            sPy8/zuvunJkDKXM7tYWTiyGWFjAqeQnAD6+7ueNx/FLpRGAru7mcoj5ebqzszil7DggeF/DX1nB
            N82rzPqrzbRayIsLhJqMPT2N83Sdy2GApwFqRN7jFPL0tF+10cDd3MTZ2AjNUkGCoyO6y9cRxfQo
            wFUbpufr1ct4ZoHg+Dg067zduTmEbq4yi/UkYidDe+kaTcP4ObJIajksPd/eyx3c+N2rvPbMDPbU
            FPZSLKzcGjKPrbJaDsu+dQO3msfZzeGY2TCvKGYQhdSYeeJjUt21dIcjXQ7U7Kv599f4j/oF55W4
            g/2e3b8AAAAASUVORK5CYII=
            """)
    def icono(self):
        return self.__conversion__(\
            """AAABAAIAICAAAAEAGACoDAAAJgAAABAQAAABABgAaAMAAM4MAAAoAAAAIAAAAEAAAAABABgAAAAA
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMA
            ZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMA
            ZjMAZjMAAJn/AJn/AJn/ZjMA/5kzmTMAmTMAmTMAmTMAmjIAmjIAmjIAmjIAmjIAmjIAmjIAmjIA
            mTIAmTIAmTMAmTMAmTMAmTMAmTMAmTIAmTMAmTMAmTMAmTMAmTMAZjMAZjMAAJn/AJn/AJn/ZjMA
            /5kz/zsE/TkD+DUC6zIB3y4B2iwA2SsA2CsA2SwA2ywA3y0A4i0A5C4A5i4A5y8A6C8A6S8A6C8A
            6C8A6C8A6S8A6y8A8DAA+DEA/TMAZjMAZjMAAJn/AJn/AJn/ZjMA/5kz/z0F+zkE6jQDzCwBuSYA
            tiUAtSUAtCUAtiUAtyUAuiYAviYAwicAxygAyikAyykAzioA0SoA0ioA0ioA0CoA0CoA2SsA6i8A
            +DEAZjMAZjMAAJn/AJn/AJn/ZjMA/5kz/z8G9zoF2zECtiYBqyMArSYCrCkHqygGqyUCqyUCqyQB
            rCMAryQAsSQAtCUAtyUAuigDvysFwCcAwicAwicAwCcAyCkA3i0A9DEAZzMAZjMAAJn/AJn/AJn/
            ZjMA/5kz/kEH9DsF0S8CqjYBr0oW3Wc/14ZqynZfxW5WwWBGuEwuszwdrzERrSsJrSoIrScFrSMA
            ryQAsiQAtCUAtyUAuyYAxCgA2CwA8DAAZjMAZjMAAJn/AJn/AJn/ZjMA/5kz/kMJ8T0GzC8Dpj4A
            t2Yo+YNn+cW7/Lys9auY7piC65eD65iA5Ihv03hfy2tSxmBFu08yszsbsS8NsS0LsysItikEvigB
            zyoA6S8AZjMAZjMAAJn/AJn/AJn/ZjMA/5kz/UYK6zwHxi0DpEUAxV8i/5Fz/uHY/NXJ/dXJ/dbL
            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
            ZjMA/Zcyqk0D12ox/+ji//Pw/u7q/OLb+vHu/OPd+uHb+t/Z/N3U+tnQ/dTJ+cu++sK0/cCy+Lyt
            /byt/se57mQ58T0H+j4H/j4F/zwE/zoEZjMAZjMAAJn/AJn/AJn/ZjMA/pgyvFUJ6npJ/93S+Oji
            +erl+erl9+vn+vHt+fTx+/b0/ff1+/Xz/vPv/O/s/enj/uPa/NnO/dDC+6mN+Fom+kMJ/kEI/0AH
            /z4F/zwFZjMAZjMAAJn/AJn/AJn/ZjMA/5kz/3Qh9Xw8/4xM+oI//Hw4/346/oFB/4NG/oNK/oFJ
            /opX/oRQ/4NR/4ZV/4hX/4ha/45j/pZw/l4m/koL/kcK/0UJ/0MI/0AH/z4GZjMAZjMAAJn/AJn/
            AJn/ZjMA/5kz/3Uh/3Uj/3Qh/3Eg/3Ae/24d/2we/2oc/2ga/2UZ/2MZ/2EX/14W/1wU/1kT/1cS
            /1QR/1EP/08O/00N/0oL/0cK/0UJ/0MI/0EHZjMAZjMAAJn/AJn/AJn/ZjMA/5kz/3Uh/3Uh/3Qh
            /3Mg/3Ef/3Ae/24e/2wd/2oc/2ga/2YZ/2MY/2EX/18W/1wU/1kT/1cS/1QR/1IP/08O/00N/0oM
            /0cK/0UJ/0MIZjMAZjMAAJn/AJn/AJn/ZjMA/5kz/3Uh/3Uh/3Uh/3Qh/3Mg/3Ef/3Ae/24e/2wd
            /2oc/2gb/2YZ/2MY/2EX/18W/1wV/1kT/1cS/1UR/1IP/08O/00N/0oM/0gK/0UJZjMAZjMAAJn/
            AJn/AJn/ZjMA/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz
            /5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kz/5kzZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMA
            ZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMAZjMA
            ZjMAZjMAZjMAZjMAZjMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAAAEAAAACAAAAABABgAAAAAAAAAAAAAAAAA
            AAAAAAAAAAAAAAAATEw/M2Z/jEwMfzMAfzMAgDIAgDIAgDIAgDIAfzIAfzMAfzMAfzIAfzMAfzMA
            cjMAM2Z/AJn/smYZ/ToD5jEBySkAxigAyCgAzikA1CoA2CwA2ywA3SwA3SwA6i4AsDIAM2Z/AJn/
            smYZ+j0Fwi4BuT4VvVM1t0YosDMSrykGsSYDtSYCuiUAvSYA0CoArDEAM2Z/AJn/smYZ9UAHtzcB
            3XZI+83B97ur9LWk7JyH4IZv0W9UyFY5wUYmxjILpjAAM2Z/AJn/smYZ8EIJrzwB64Jb+aiT9p6I
            9ZZ9+JV9+pqB/J2F/Jh//JR62Vc2pjAAM2Z/AJn/smYZ60UKq0IC9pp+/pyE/6qV/5d+/4Nj/2xH
            /lcu/kcZ/Fct3TwSqzEAM2Z/AJn/smUZ5EUMs0oG/bqo/qWP/7ur/6iS/5R5/39f/2xH/1cs+HNR
            4DEFrjIAM2Z/AJn/sWQY2UcLw1MU/dfO/rOh/8u9/7im/6SO/49z/3tb/mZA8XVU5i4AsDIAM2Z/
            AJn/sGIYzUkJ1HNB/uHa/sa4/9nP/8i5/7Wh/5+I/4xu/ntb52E97y8AsjMAM2Z/AJn/r2EXwksI
            5Jt3/tvS/tzS/+fg/9bM/8W2/7Cd/5yE/ZR64Uwk9TEAsjMAM2Z/AJn/rV4WuUsI87ei/s/E//Pw
            //Hu/+Pc/9PI/8Cw/6yX+p+I4TwP+jUBsjMAM2Z/AJn/r2AXu1IN/NzR/sq9/tDE/tnP/tDD/sS1
            /rem/66b9J2E5zYD/TkCsjQBM2Z/AJn/sWUZyWEh/efh++nj+ezn+urm++jj/ODY/NPI+8i694tp
            +D8H/j4FsjYCM2Z/AJn/smYZ/HYo/Xwy/nYr/nYw/nQx/nQ1/3A0/3A1/nI8/lES/kcJ/0IHsjkD
            M2Z/AJn/smYZ/3Uh/3Mg/3Ee/24d/2ob/2UZ/2EW/1sU/1YR/1EP/0wM/0cKsjsETEw/M2Z/jEwM
            smYZsmYZsmYZsmYZsmYZsmYZsmYZsmYZsmYZsmYZsmYZsmYZjEwMAACcQQAAnEEAAJxBAACcQQAA
            nEEAAJxBAACcQQAAnEEAAJxBAACcQQAAnEEAAJxBAACcQQAAnEEAAJxBAACcQQ==
            """)
    def edit_copy(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI\nWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QoaFAgvgxQ0mwAAAX9JREFUOMuVk0tLAlEYht8jM2Pa\ngP0KzwjdFv2PCFq2iKB1F/BCtrBFkXbbREREG7E2Bf4EMbM2gWUwo7+gmjAFN83ttGl0Rkexb/Wd\nw3kf3vfjO+ToJDOv6/osRijBz71trsXvnHecYRjT8ejWKHqkD/YmAbgBdtNqNcEY6xMRQgAAodCE\nJ5RzHmq1Gl6rlYXGd2NmkIv9zG7K7nmev3UBJElCsVSY+kekRRdAUZROjFarOVRsR3IBKKUolgqd\nsyzLnuJIJNI/A8YYZFl2DdL5cFC5AJRSlMrFoQ56oZwttiwGRRnNQTA4jna73QXoug7GGMJhivJT\naagDSiWYpoHKS6UL0LQfBAJjsCw21O7l1QUeHu/dEQSer56dn7oWhzHL07YoilhZXoVlmVC/VOSu\ns+A21qN5AHnHcmwbhuHrFTtLVVXkbrIA8OzzGpKm6fD7/RAEAaIoghCCer0OgODj890WpxKx5Bzp\nFR8ep7OmaS55fay/KgAoJGLJHQD4BUJZpgMViPfYAAAAAElFTkSuQmCC\n""")
    def edit_cut(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI\nWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QocFh0xaEFkXgAAArRJREFUOMuFk11Ik1EYx59z3nev\nr9vUfaXbbPgVaHjRVRB0YZRJV0XeZCIRaGmWWKhpgZAElaV9gYgQlBjoEPRKkCS6DAK1MG0zNvJj\n7zZ1m+51X+92zttNzmFa5+78/w8//s/znIMg5TzrfXIOAN7zPO9tunm7dI/Xz7LspTvNrbpUHade\nGIYZu9XYrI1Go8t9/a87Uz0Fq7hw5nS55sWrnk8HAggh/E+HHdfV1lcQQo7t6E97HpeZc82m7ZCI\nKKUnDgRgjENLS7+AT0tDsVisdCcFy7JThYWF4HF7KKXU8a8EFTabDVZdK6iutr44kUic6nnePVBS\nUqJAgMHhdAAAWA8E3G299xljvLy4aAc+jUeSJB3X6/TXZAqwvrFGAWCiraXj4YEAAABKaeXCjwV5\nbc0DjTeaVPFEHIliEObm5iQA6Npb/xegraVjGmM8ZF+00WBwC2s0GhDcgizL8ru2lo7p/wL+pJia\nnZnGTqcD0jkeMt8ORhBCb/arRXuFMaOxl1B6Pb65qSblZTIz+REVGHNAIHQLITRQ6fG07wsYM5k6\n437/g6MmEyQoRd6tTdkX3h5mZVRVkJ3D8BxHJVkG5/o6KLKyrla63UPJFsbN5hrJ5+sqNhrpwsrK\nVDASlgJBEdfEaU2UIzqWwTQQEhOO1dUPR/R6EvP5BsfN5t2XOmowCPNFRWSEYe4DAMxYLCGrUpnY\n8UcYhnzJNQcBAIYxbv+Wn09GDQZhd4ixmF6SJFJFyKMJleqlgmV5hLE9OWmOm1Hz6arJjIy+y5R2\ngyxTIMSwC+A4Qa1UMl/z8mImna5pXhC8iszMK8mPpNU2fHe5Ng4fOtQwa7HECKUYMA4AADAAANVa\nrc/l95/0SxIbAJA5tfrsRUFI7twqiu7q7GyPNxDI8YfDGl8k4lOoVOetouj+DaDzOgfcNME8AAAA\nAElFTkSuQmCC\n""")
    def edit_paste(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA\nB3RJTUUH1QoOABwVr+LxGAAAAdBJREFUOMuVk7FrU1EUxn/3vTSCJDGN1JQMhSIGXFy0amIE0RJw\ndtAhOBRFbR3ExUGXgjgIjvoPNIO7m6hL1S66OCmRUqjRSEJeb2zQRu85DqExL20gftv9zj0/zvng\nGAZUKpWM73vPnZPZft/3vRfOSbFcLmu/bwBuzporBh4qjCsedvISudwRPM8AIKKsrHxgX+0pBgFo\nquqtxy9ZMvNnifieCS6cORj70snwLsjStB2mp6cwZhsgrK2tk0xEOZr8zKS/zrPXq1ZUUxEg5nlm\nLBrxeV/Psnj/EUEQUKlUQqvNzR0ilUpx7+5tLma+IaoxIBrp/9TegkQigaowM3NsMB7i8Thbf8Cp\n6Xk9gGooG5bfvA29C/kcuynCEJ0+lecfXBBxwwG6S2F7AlVFRcidPP5/ExTyOUQEEUFVsNYyMZEe\nDdDfKNJtbv1ojT6BiOtBql+rNBr1HSGHAQM157qAVsvSqNcpFs8P2xRv2ATWblD7XkNEev71+atc\nnloevsLeMaUZNEmnM6TTGbLZw1i7gapwY+Far9k3GgJsiujv9i+350TyIw8W7/DT7YymsP8Tq+0D\nACS1ijFmU1U7BmDhXPcaMYwzglS71/jkFUt/AU/m4Zh4acTaAAAAAElFTkSuQmCC\n""")
    def edit_redo(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI\nWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1gcaCicVP7jtIQAAAdxJREFUOMudk01rE1EYhZ87X02M\npEJMY4MfbTbVdtPSKn5UYw1CqThuRCuCuBpwrTvBv+B+Vt11KUQKhYrFUrpqpKgbwU11ISliTCZN\nmslkxs0YJ51Bgmf5Xp7Duee+F/qQbmqebmrTUWcS/WtbN7XCfxs8fmAAvNFNbS44FxFxB4A8sAhM\nAZMBA5aWTYAbRcNeDxnopnYBeD4ntFS2cHVYTY3mEAJVjmHZPyl9W+HK6L0eExGAF4AXj/L58/JQ\nTqrZZbzap550H5s1gK7JuT17VvjwBPDy4bXrN2OZM1iVdSxPI+7aAAw6DTbbzt/ihMSlkbssLZso\n/uzpnbPjk7F0lvqvdyRaDRI0GG5VeEUCR+rtOj14snsNBWBA1WaPj02n49Z7svtVdqQEmiKoHYkz\n7kMXFTDrFpljp9lc/dDtQAHouG5GyIJUw2KrVPfWWpXQ60xcPhGCu3vgdJzk0cZXtnd2WWu1LeAZ\nMFU0bFE0bAHwNjkUgoFuB+w3q+5KXUjA/aJhrx5O4MMzRcMuRW6iqsgHgBcF+wrBwQQbzb2yWpC9\nGKY2f9jkzzWiJAOM3ZbdLwft+q2Z3I/UbvmU0NWtz687dj9/JLiJI8ACUAU2niTd7wK8+UWn8y+D\n39dLugVezzXeAAAAAElFTkSuQmCC\n""")
    def edit_undo(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI\nWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1gcaCg4AFiOWIQAAAhdJREFUOMuVk09okmEcx7/P877P\n1OX+6MYa0ojWwfIQFIRBgxUEQrBDeAiCYkRQXTuMPHgox4wdIrp0qVhBEDTpUCwWwVKMWnaKlLRo\nDXITXL4654bv6/M8HcKlm5Z9b88Xvp/neX7P9wGaKDoFiRakbjXm7qGXKciiRdHahd/HbExB1u0N\ntZr/cwK/j9k8TiPn9oaAwtXNa+ikJ8MFzYC2xcPJ7MXxCb1UCyBbw0ZuHCrVAIsXkBVwLgGI8pvZ\nx18ZBXmVKHgCQeNHFaD4fazd4zRW3d4QjJ/XQShFuQyAL0JfT0FbiUHKkjroOtFntii9NuRPD+yr\nvI5ExTIAKBMXhF4NU6r8pqoMUkoIwSGEgOBrKK+nYLKYyI6uXZ2dYu3Q7v36o0hUGPRlktnnQ16w\njpMAAM51LHz7iMXvcaTTX+oGVtTisPe7YG5nB4ad3eHtMxgZw0LiJva4rkDwYl1YFO8ik2Uo6xw9\njkv49Ha6dPxs2qoCQCBoaPAxOzCZc4+MAQBiM3fq38tC4DpyGYXMA5jMOgiRal0PAkFDm00y+/yz\nyc3M0CjI0CgIgIOlvDyVmLv9vm/gHLjoAJHShL/VuFGVw/fheDdN5eryDRF5aJPbmli7cyN/+DyW\nFGGVG8U4hGrPNwU0g0SnMNjtOCy07BIA3Gr4mf6ho1079858jj2pHDujXftvgGzrt6Y+PH9Bde1p\n1fsFBRbiJSu+JBQAAAAASUVORK5CYII=\n""")
    def x_office_spreadsheet(self):
        return self.__conversion__(\
            """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
            """)
    def x_office_calendar(self):
        return self.__conversion__( \
            """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
            AUEAAAAldEVYdGNyZWF0ZS1kYXRlADIwMDktMTEtMTBUMTk6Mzg6MjEtMDc6MDAmCoZFAAAAJXRF
            WHRkYXRlOmNyZWF0ZQAyMDEwLTAxLTI1VDA4OjMwOjA3LTA3OjAwTjbCAAAAACV0RVh0ZGF0ZTpt
            b2RpZnkAMjAxMC0wMS0xMVQwODo1NzoyNi0wNzowMFb7sEwAAAAydEVYdExpY2Vuc2UAaHR0cDov
            L2VuLndpa2lwZWRpYS5vcmcvd2lraS9QdWJsaWNfZG9tYWluP/3qzwAAACV0RVh0bW9kaWZ5LWRh
            dGUAMjAwOS0xMS0xMFQxOTozODoyMS0wNzowMHm78HEAAAAZdEVYdFNvdXJjZQBUYW5nbyBJY29u
            IExpYnJhcnlUz+2CAAAAOnRFWHRTb3VyY2VfVVJMAGh0dHA6Ly90YW5nby5mcmVlZGVza3RvcC5v
            cmcvVGFuZ29fSWNvbl9MaWJyYXJ5vMit1gAAAABJRU5ErkJggg==
            """)
    def save(self):
        return self.__conversion__( \
            """iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI
            WXMAAABIAAAASABGyWs+AAAACXZwQWcAAAAgAAAAIACH+pydAAADK0lEQVRYw+WXP2wURxSHv/Uu
            9nGBA4dDBBkkXKBQGOGkpEiIRBkJCP9EgyhShIIGJJQKUUAHJUWcpApKmhQ0iRRQIiRLKUgahJQq
            kYWNbSFDgS7ny93OvJdid/ZmfXd7IK8rnmR5dnZm3m+++c3ODbztEbjC1Mdf3Gm3WxfRbt1GxabR
            yo9/zX51GiBylaYTX5iZuRWMRBGiytTst6CKioCq9yeoK3vvNH2XPfv9gNmPLqEoIsq1L6+fcnkz
            ARpIIAoXznzKZ1e+oX7zatZ5/ZwDHrxzElXlyPSu3KvIf7AinLj8NSLC1LyUil1u/w6qiM2PmxMg
            oohDV3KoJEtnJT92DwG1gtJtNDc3t67Ek5OT6eSSidlCAjYl4AlwA5RGwNohBCRPoKx4LQLWSg+B
            spagS2CICV3DtQOUQUBVsWaAAPUJbOAuMDKIgHoe0I3ZBaqKFJqwD4Gyd4EpNGEfD5QVXQ8UErAb
            74Fh29A1PH/jVxSyky/7D9mzI+W3Sap0TT/QtK7QA+J5wA0uLx7TWX6ESr7jsBgZCQl2TGO2vJ+c
            yiSCCgkYj4CbbWf5D04cP0a1WiUMQ6IoIgzDvmVrLXEcY4yh0Wjw3d3vker+HAEz2AOa2wUZOjHU
            ajWiKOKnn39heWkBgIm9+zh39hRhGGKModVqZcnjOE5MJyadUJfAkLPA5gmkXqxUKoRhyPLSAq2d
            xwFYXLiHtZZ2u51L7JfBnQGJT5SCL6EzoU/ACRgbGyOKck0BWF1dHZjcGOO5PzUqSly0DY0ZTGAt
            OoBms5lL+FoEir+E2kMggGx9yyAwRIBNfrdlIhIBbqaDBLyZB/oLiFR087P5RfbuqvN06VX66YQR
            L9GO+nu8XLkHwPbxOs1ms2fWvogeAprzwFag4QRs+3dl7uTsb/fvHv7kaOXAvt2BiiAKf893CXz4
            wUHi+ECWaBAB8Y7c3Ttrma9ExCc5DkgAhEAdqNf3TB8enzg04yM6ONFgPfFkcWtPndjOw3/+/OFz
            4Lm7htWAd4FtwBZglIR+mdFJx/wPaAAvgBX/Hjiarks1LZcdjn0LeAW0gcKLaNmX1L5n/P/IsHOa
            EPxs0gAAACV0RVh0Y3JlYXRlLWRhdGUAMjAwOS0xMS0xMFQxOTozODoyMS0wNzowMCYKhkUAAAAl
            dEVYdGRhdGU6Y3JlYXRlADIwMTAtMDItMjBUMjM6MjY6MjItMDc6MDBNE2XsAAAAJXRFWHRkYXRl
            Om1vZGlmeQAyMDEwLTAxLTExVDA4OjU3OjI1LTA3OjAwZxOq0QAAADJ0RVh0TGljZW5zZQBodHRw
            Oi8vZW4ud2lraXBlZGlhLm9yZy93aWtpL1B1YmxpY19kb21haW4//erPAAAAJXRFWHRtb2RpZnkt
            ZGF0ZQAyMDA5LTExLTEwVDE5OjM4OjIxLTA3OjAwebvwcQAAABl0RVh0U291cmNlAFRhbmdvIElj
            b24gTGlicmFyeVTP7YIAAAA6dEVYdFNvdXJjZV9VUkwAaHR0cDovL3RhbmdvLmZyZWVkZXNrdG9w
            Lm9yZy9UYW5nb19JY29uX0xpYnJhcnm8yK3WAAAAAElFTkSuQmCC
            """)
    def save2disk(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI\nWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QsKDTgPGbLEcAAAAIx0RVh0Q29tbWVudABNZW51LXNp\nemVkIGljb24KPT09PT09PT09PQoKKGMpIDIwMDMgSmFrdWIgJ2ppbW1hYycgU3RlaW5lciwgCmh0\ndHA6Ly9qaW1tYWMubXVzaWNoYWxsLmN6CgpjcmVhdGVkIHdpdGggdGhlIEdJTVAsCmh0dHA6Ly93\nd3cuZ2ltcC5vcmdnisdHAAACV0lEQVQ4y52ST0iTYRzHP+/b/DNz8s7ha1q2iZpIHSI0tgQND2mQ\nROEhhMQiqFiNeepgYR4MIQPxIEWHpCCEFQVF3SKhg2Z5KLKDmmhZhuRwbqXb3vfXYbYSLcjP6Xme\nL8+H7/PjUc51XLg4Fc5X5+ajC0ABUAfsTFFl2Zb+/VtWWrSvv/NKK39BqfH3NLl2lLmcufrk7sIc\nv9Nu3ROJG4x+WeT10IA59nGWUvub7b3td2fWFXjbOntjobmzcVGZNTR+pOWwyZJCY+0+ivKz6b7/\nAuPTCK7U+fXut+Nt8cn05wkREZmYGpWh0Qnx3Xgi7tNXJTA8LT1P30rDpZvybnJG/iQcDovP7xVL\nmsVga66LYDCIlpmLqixglSgAI+Oz6JkWvs4v8n7iA1uyrKAACKmpqQBY4jEQUzBMk/rWW2s6Dk0G\nicUNugKDdAUGAXjccQIkkasAppiYhknPGQ8AzceO4HGXs7QUIc+mUumuoKmhHoDjNcWYhomI/BaI\nCHa7Rn6Oi2unyunrf0CpqwAVBRUFd5mT2/ce0VhdyOHKCjI2Z6wWAITDYXRdx5lXkpR4dhVR4tpG\n952HNFYXcrTKja7rRKPR5BMtAKZpEolEANB1HV3X6T1vpeV6gOWYwcnaMpoPHUBVVUKhEJFIBJvN\nlvgHPr9XKsr3IqwM+D8YfvUy0cDjrgSRFYOSmLAiIMrKNqEvKS5mfHwMQUH5U+BwOHg+8CwZCLKm\nzf6qGgCyHQ4QJZlbADRNIz3d+s+6ml0DwK7ZV51bfi3qag+yERSf33sZaGNjtP8Elb70qz97tp0A\nAAAASUVORK5CYII=\n""")
    def view_refresh(self):
        return self.__conversion__(\
            """iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI
            WXMAAABIAAAASABGyWs+AAAACXZwQWcAAAAWAAAAFgDcxelYAAAE40lEQVQ4y7WVa0wUVxTH//fO
            zM7u7CLvp8hDrEWCWhShom181DRpjUnThhDUxDQVsH6ybZqYNOmXpompSZPWoiCpsQU0pUmrjX0k
            xkepVYEgaKtAqA+ERUDchX3P455+YCE8bOKX3uSfm9x75jf/e+45M4yI8H8M/ixB5eUt0rPErd93
            OqfsnZYEAGBPc1xa9c1yRVE/BMMW07TSBUGROPNzzkYtQRcEiRZBgd876qqM6Wde3HsqVXD607Sw
            pbOh8sEcMGNgZe+ebgBYxUsvLLGtyE2RXU4VnDPouoFAyMCDRxPWjV53YGQ8IDGGQ36ufO6SdA6d
            t1tCLCcmsjvqdg/MAW/Yf/pETnpc+e7XVmkRw4LXH0aMpkJTFUgcYJwBNOXAH4zgUuf98PW/hnQS
            cG8syl56q3/EmPAG868d3zkoT0OLq78tTXBpb20rWap91dIuxjxBzjkgLCJiMNMSXaHSwkxn0fNp
            EhEQMghb1uXZiwsy7f0Pn8S8UpzNunqHTV1IYs7l2WWlZpFLdTac6aTJgMEcdiVsCfHdtbpKHuJI
            dY/4t51r7fv+k69bg209w+RUJQyNh/AkYGJdQQZTZA7LEpDt4blgMLw6MDzBEuNiPMty0m7ouukB
            xGcAcLO20tPeUNl2pbaiwtCtDb9d6Ws//kNHMN7BkZWs4dKtUSgShyUEi8x3TAKq5lCHsjJT6mI1
            eyMY77PI5plfMW31lV26YR6cDOhSjEPB0HgIAoBd4bAsYoqQBQDM5NgSIpjkcnwR47D/pOvqY4qw
            kzFLUibng4urm1YqsnS25s1iNTleQ3qSE5sKU6AqEkxBzGbNAzvSM3LP4rI4s+d1AQCoWo6F0MZ0
            RvxXyyLtSEt7hASBCCBMzUKQTbcCYk6DlFQ3jzHA9bSOIoKPcbHtiS2xx+UbcfxX5ykEtf3knlEi
            kDxrPa7x4+2yTeYAGBgDwrqJj+pbI/dHJt67fmxXdzQuMuW+XgHitbLConBijB7f/c/DssHRx/VE
            SJqTChAxu03GhVsjYCCU5Sej+fydyMCo70jbsZ2N893JwpkqqeKo6vD9OBEWyV6/v9omy9b0/qxy
            m3JpmAKZSU4wAN39Y8QZW1ny9uklC84tYZFlifUTvuCu2/cGP/AFwjmM4+7Mi2cMgxgDsDo3DoPj
            QQx5OA7v32xvPt+z9dyV/p7SmuYvhUUdIDbAFUsmkg47VCWu5+7QJpsiUWKsZni8oYYF4CnTDMGQ
            joLFsYiYFjrvefByUZZUUpChddwZft/92Bd2j/nYuDfolGwMqYka8nNTkBTnZE0/d4U1U29aAOaM
            sfuPJnGw9pKXM/DtG5fZNq/NtnsCJiwCivLT5UIrzcXYVP4MQTBNAa8/gqZfbvgtwzhw8cSe8IxJ
            IgJjTFpX1WjEOm2B/q6L290dZx7lba7akbg4r2bVc+mZBXmpSlZaLHM6bIgYAoZpYSKgo6vXLa7e
            fKgHvSOHuk8dqAUQBhAmIn0abF+7t9Hjd98u7z336d8AHFHZM9bsWJ26YmuFosWvAWeqU1WMYMSU
            iAAR8f0x2td6dOBqczeAUFRBIgpOg9mqXUffuNm47zIAOwB1lpSoJMmZqCRkFiYEPcOewGifB4Ae
            retIFOoDECEiWvBrYoxJs2DTkgFImPrMW1EZUekATCKyZnP+BSlpXJoO+4NRAAAAJXRFWHRjcmVh
            dGUtZGF0ZQAyMDA5LTExLTEwVDE5OjM4OjIwLTA3OjAwgH2N8QAAACV0RVh0ZGF0ZTpjcmVhdGUA
            MjAxMC0wMi0yMFQyMzoyNjoxOC0wNzowMGfsPUEAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMTAtMDEt
            MTFUMDg6NTY6MzMtMDc6MDAnq/RLAAAAMnRFWHRMaWNlbnNlAGh0dHA6Ly9lbi53aWtpcGVkaWEu
            b3JnL3dpa2kvUHVibGljX2RvbWFpbj/96s8AAAAldEVYdG1vZGlmeS1kYXRlADIwMDktMTEtMTBU
            MTk6Mzg6MjAtMDc6MDDfzPvFAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAA
            ABl0RVh0U291cmNlAFRhbmdvIEljb24gTGlicmFyeVTP7YIAAAA6dEVYdFNvdXJjZV9VUkwAaHR0
            cDovL3RhbmdvLmZyZWVkZXNrdG9wLm9yZy9UYW5nb19JY29uX0xpYnJhcnm8yK3WAAAAAElFTkSu
            QmCC
            """)   
    def config(self):
        return self.__conversion__(\
            """iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAQAAADZc7J/AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAA
            AEgAAABIAEbJaz4AAAAJdnBBZwAAACAAAAAgAIf6nJ0AAASSSURBVEjHjZRtTJZVGMd/9+vzwgMM
            KCHSwjewF2S6VtpCcTVTV9bMD87Nl7mmrZaftFZqPbJw2pxzfXDpnGuWNsdyk62ZH+yhdIoL08xg
            YSmCBCEOAZ+3c5/73H3gBh4IWuf6cJ9751z/6zr//3VdGhOunX97k4yUGzSu7Jg78S1z4iM9dy2h
            YJKvSvmPpU908MnjJibdhPHsXQX/C2DnuuqO6jlDf7KiQEk0XPIc8cTwnTVRr3pDJoAxtKl+L7i3
            PL97XVXy+4ZAQeU7HC4zJ2kQ4J7Ws2pRoqq5KnvpN9mbl5h3Fleq2PkhP23wE91s7FttBEhyOtXr
            6HqJ9aRdwgM8goRooynd4rnBee4CAxIcUKz56PgoEnUV8MK0YbMi2BosJoygHx0LDUkJpYF+Ujxk
            pIEAthKTxmTgaTXnK54rM/qwycPBxcywwXd6SBQ23zk36j5YOYZEzdNW/pISZGGQwMPGxvLNBBTS
            h22h5V56/TgqbOtUZxtV/rCbhY2FjYHCxUWhUJhckLIu+mAEQBvaRHOMO6uyA0g/7QABYIAsdATS
            B7Do51i/fHQEYqQSV0628hnAxsQgiKIu9TvGgJs9k5eDug+RJJ9iq20FRzMy+Cxwv1SVcWKZ/rgf
            38Li83jyqNgSTUTD9t7g2jezkkg8FBZdnML+WTXIn8yz29u16jtecSRVoBXZ8/UkOiYmQWLpy0c+
            fHsoyq4Dsze8EBjw2cgnSTddXqu8Kz6OmF7RRs0KuUAaE8MX7aoUu0eIEruvr10YGFRC0o6LTolW
            Zh1Lg+kZYR6A72yioYB0kK6Mgu8SQRBI3xQaBhG8LNChGUUOEUJY4EuWk9DLM7QujyQcHAQCQTH5
            uNwmJjwNTP3dH5arCqcg7L1lar5YDpWRM4cOztvkABy0eg49GxnwMzCIcxyrQV1xr9E40kxh88Ky
            ijIcFAoIcSrZ2uJs825oM42ax0qXhToQOEhy6aTx2+2vjGnnemeBkIufsgYBXBzKrVBhYrm3Ke+N
            Z6Y8b3WSwkHiUsTFZGJX/a//KqSsE237ukO5OHgoFL1M18qyQRKnHeErEKGPXsOrHacXtsbljzFl
            DVe+pJ9u/qKDHlIIBA4OSdJ4tlk4DkB0hvlSlR4fplH45mTY4IyoUFqtp43hIGoHzlUWTtFSaIRR
            /ovlsKskm2lEiBOnTGt7+MxA/aVRGRhfZM2Yq8Wx0GjwBsgnjO7H18ljGhYnnQY5jRwc5gS8/WMy
            eDEoXptl5PInJ9Ot15qz2j3DLCJCDzpTuc2l5PV056eJ3tbps0ybM6n06nNNY+fBFrsm1+i9+9vG
            r5uKc5a++sgSc/56mskiyUV1c8fZWEc/zqaqyfvdUHLrngMI5CgA7PdXmQtra1oG55mNXX369dzb
            FHBLxQ4f/hIHQRqxqGBq4ZFzpEnjjh4ock8tddgEMFAoPNF2vzyXHO45nTcBhYvCjbXH/kAiB90z
            ARRJXFxcJA426fjVvqdnaw595q1G+jKUFUPRRwMACASGP4pNUX95zWWQJJqacf1OdhCjPDI4GG/p
            aICHhzfRlX8A6LAajk+oHXMAAAAldEVYdGNyZWF0ZS1kYXRlADIwMDktMTEtMTBUMTk6Mzg6MjEt
            MDc6MDAmCoZFAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDEwLTAyLTIwVDIzOjI2OjIzLTA3OjAw62Ru
            WAAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxMC0wMS0xMVQwODo1NzoyNy0wNzowMPCMu/gAAAAydEVY
            dExpY2Vuc2UAaHR0cDovL2VuLndpa2lwZWRpYS5vcmcvd2lraS9QdWJsaWNfZG9tYWluP/3qzwAA
            ACV0RVh0bW9kaWZ5LWRhdGUAMjAwOS0xMS0xMFQxOTozODoyMS0wNzowMHm78HEAAAAZdEVYdFNv
            dXJjZQBUYW5nbyBJY29uIExpYnJhcnlUz+2CAAAAOnRFWHRTb3VyY2VfVVJMAGh0dHA6Ly90YW5n
            by5mcmVlZGVza3RvcC5vcmcvVGFuZ29fSWNvbl9MaWJyYXJ5vMit1gAAAABJRU5ErkJggg==
            """)
    def water_drop_big(self):
        return self.__conversion__( \
            """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
            cuf5qi0dG0bXKDTCoW30yIBRW3sEQh69NrwyPjbCYwyMx4HPpQn7F6PN05TLE+N3vv0Gh7Noazrh
            +l6iz69I7NwVafFL0FGPkLJRwui1Rj+IeLtfjNtY1qtAa7IjixU4PBmdX90T33p0i63g4nXH5v1j
            ZkA1PnPJqazvJTF3HhT8isPT0RcSNh9taNRea3reG973mvr5RBh4iyVe5I9vAp+ay3nsXFu5KOMX
            DQDAr21fw9qe5QPiXwvudPib6D5XU54R3SvxalJ3nNY1CNEr79YhkLdD5Eh07gPuuuhU++d+gr93
            XXexZhz/z+S+8twhzl8deOlQflYn2B2pcXsQm4NJRZts1NxMJjpJC9O/aohUelJqTHT356LzRw73
            GbwxD7zn1MUbvyQAVOP+Fw/jThqMHwnitiD9RCI2BsOqBmoYj3sTgXbPsLmuKO3P3dnj+G6He915
            FpFfuPb4DF9yAAB27z1MR5A5/SBtD+K6IK4Kpq1BrA4iaXnfRm2wZj9RMA+8CTwL/L3DI8B3gbl3
            L5HhywJAc3xj3xHcSUxsNHFxkC4z45IgtgZ0holO1d8vN1AGBq9IfE/wOOJfgO8Ar8LSeXx8/B+o
            njRP+KkGrgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxMC0wMi0xNlQyMjozNzozOS0wNzowMHBvbpMA
            AAAldEVYdGRhdGU6bW9kaWZ5ADIwMTAtMDItMTZUMjI6Mzc6MzktMDc6MDABMtYvAAAAMnRFWHRM
            aWNlbnNlAGh0dHA6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvUHVibGljX2RvbWFpbj/96s8AAAAQ
            dEVYdFNvdXJjZQBXUENsaXBhcnThHo5hAAAAJHRFWHRTb3VyY2VfVVJMAGh0dHA6Ly93d3cud3Bj
            bGlwYXJ0LmNvbS80l/SfAAAAAElFTkSuQmCC
            """)
    def water_drop_1(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABGdBTUEAALGPC/xhBQAAAAFzUkdC\nAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAAZiS0dE\nAAAAAAAA+UO7fwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAl2cEFnAAAAIAAAACAAh/qcnQAABZZJ\nREFUWMO9l/uPnFUZxz/f57yXmenutrO7UEqrBYRNLYqJSiVSDAZMTUVFTCERU4hEExP/Bw0/aKJG\nYvzFXzCaeImRgG4Af6Em1oKJ8RJBJWlJgSWN66VhL93uzuWcxx/ed2aX9DLrxvomJ+/MmXPO9/t8\nn8t5RmzxOfDknDxxuwO96M//+YG9vpVzbKsEFtZSa6kbP7HYjUcWu2mC77y8pXOyLW367kkWOnGf\n4FB0tnWTz7LcPfZ/UyC5F0vd+NHFbrpxuZf2dqJ/ujHVmpj58etXnsDuH5ymCLYP9KlMtJqZsvHc\n7mmX4WAnuq4ogXf86DU60Vtjmd23vbCb22Vgsgy0y7C7XdpndhTaefjpM1eOwD9XnfHcbp0o7Ei7\nERqTzcBUIzDdMJssw6F2aR/rJ8Ijv/rHps/cdBAeeGKOlX6aMnQ0N2YamVEGUZgIBkGaCuKhzPTC\nzGS26ZTYlM/u+Pkcq13PzPRgZvpGM+iqZm40gigMMhMmIegE8Vhm+tquVlj68q1T/xsFdjYL5r23\nP0ifawRNj+WilRmNTJQmMhNBgChB95t4YanTfxoYWZxGKnD37Bn6nnbk0qPt0r5w/URWjuXGuV71\nexlEbsIEQiTcgV8G+NJ0M3v18/sntk7g3T87w2TuoQwc2TuefevuPY1d+ydzeglOLfZ5YzmRqSIQ\nrCbgTnTOOXxV8O2J0s4fnRnfmgve24a/r+rmq5v2xXuua+667ZqCTh9Wes6ebRkxJXqJioBAguQQ\nk4/1naOO/76T/Lkfnl7xz96w7b8jcNfsGebXmCiMh67dFg68azIHh7Xo9L0C3V4YncgQfPAkF9G5\nKbk/AryUi/lL4Vy0Duz76Wu4ewjwkfHCHpjZkTfGC8MknMrKvoNJlAGKOh0HaVkEUQZCYTqUSZ90\nyH9xemXzCtw0ltFNenswPbyzFa69ZSqnE521COe6sNKHTqwCqBgE4AYJqjgQBjui+4MOzzcK/8um\nCSz0Uj6WhXsbQR8ypNeXI50InSTW+hVwZiIf1oBqTlArJKJDX46S3pfc7+30dArojHTBB5+aIze7\nLpjuawRNSPDqUuL0krPYAXeGkT8YA9mH71CRy01kRsukj5u4/pm585tQwDGDO3PxnmZmNENVcoNE\npuGh6wCCYGB1RjtO8uq7vJLE5e8E3ZHgJJAuq0Am227SwSJorAzQyEQzE41AXfMr2SsykNeW5wGK\nUMVEbiILkAsyg8wYC+IDBuMjFTBxVWbMFEEqa+vLYDWoCEMFqhJcVBdRVYrrGOgnkFcjVVmjJL/R\noQ0sXpZAEBNB2p7XQTawKAhMlQIDwKxWI6/nUJUBohI6GQSv9pk07u6tkQoEUz834sDfA5/bWwhQ\nK1GBD9ZQZ8AgG6L7cL2Jvos4kkBuLAbT2crK2nLW00wXJVKREFWBcpzoA2DVe/zfLi2PTMPMdDY3\nXjaRbHjAhrGBjAnCsCaIPGxUa+N6jwZ/k3hzJAEnLefScZMWqC0e1Lh1cK3P1++h1Fx4xUr6l4nj\nMbI2kgAuz0y/DsZxIOHrXYUPh+N1hA/uhugQU/XZAffBaqLgmNBv0YUNygUEZg/vRtJ8YXpc0qno\nXgP6W4gkqqpYgTu95HRTdVPG9fQD+KvE9xKcvWtPk5EEaoCUm44F8U2HuZTWrUo1aH3v009OL0E3\nVgR69VytxivA1wUnuER7dlECj995NdFZzcRPgvRogpeSk4ZS16PvVdGprIdurIj0EjG6/8HhKw5P\nOnRvv6ZxMajLt2SPvbhAuwxFK9OBRtDDhenDZWB3YSqLuiOu2jERKv92HN5Iieei+/cT/DEl+rdM\nl5fEuGxL9uL8eQ6+bax7/5/ePDH7/umTwG3JORzhYHRu6DtNOXjylSRekfQb4FmH35UKZ1c9cmLE\nX5//AH8LNAsvJlhUAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDEwLTAyLTE2VDIyOjM3OjUxLTA3OjAw\nhe8pcwAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxMC0wMi0xNlQyMjozNzo1MS0wNzowMPSykc8AAAAy\ndEVYdExpY2Vuc2UAaHR0cDovL2VuLndpa2lwZWRpYS5vcmcvd2lraS9QdWJsaWNfZG9tYWluP/3q\nzwAAABB0RVh0U291cmNlAFdQQ2xpcGFydOEejmEAAAAkdEVYdFNvdXJjZV9VUkwAaHR0cDovL3d3\ndy53cGNsaXBhcnQuY29tLzSX9J8AAAAASUVORK5CYII=\n""")
    def delete(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz\nAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIaSURB\nVDiNjZI/SNVRFMc/5977y/fkZYMkhK46iDx5LW4Ngi1NOWRB2BYRDba7GI6llaHRW1zKoMaadSzE\n3B6IWG8QHUwlEl++d+89DT/fU5HMA1/u8D1/vt9zjxSLRQvcSZJkBGjlfPEnhDAbY5xxIvK4ubn5\nSWdnZzabzSIi/62u1WqUy+Wx3d3da85aO9LT05O9vLiIW1gA1TObqCqhUODS4GDT/Px8v4sxtuZy\nOS7MziJbW+fSb5eX8UNDJElSMwDGGMT7o4zePLS1oaopcjm0rw8ymZQPAWMMAAZARFBVYozE7m6Y\nmYb379CrBbTlIky/QiafofeGiSEQY2w0cHUFMUY0BNjZxlQqkM1iJp6iP7eR9vZ08OoqGgIiclKB\nMYYQQoofZaoPH8H+PjRlGsV+5jX+0+dG3ikLMUbiIem/r6E7O0c7CQG/tEQIIbVwqEJEjjWok86R\nKb5BOjrSb6tWwVoyr6aQfP7fClSVECPSm8d0dQFQmZjk991hdG8PMhns9YHGEuu34k5Z+PIV83KK\nuLFB5cNHAH7duk1m8CYHc3Op/GPH5uo2Y4wpvGfv+Qs0xsYKqqUS1VIp9W0MRrXBGRE5qFarJAMD\nqHNokjTe6BzRWqJzJ7ikvx9VxXvvnIi8LZVK9wujo65lfBxrLcaYBk4c2SG896ysrACsOe/92Obm\n5pX19fUbInKk7YxQVWut/Var1R78BWN4K9NzAEw1AAAAAElFTkSuQmCC\n""")
    def exportText(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABmJLR0QA/wD/AP+gvaeTAAAACXBI\nWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1QYYDQkr4Wx8tgAAAZhJREFUOMu1ld1qGkEYhp9vVo+a\nnCriDSgq/lGStb2bXkQJpD1IYjD2wvpHQQRRPBHaHiwoFAIhB2X360Hczbgb3AmmHww7s7s88847\n7zDwn0rizmg8vAA+HAJT1cuz9+cfd16OxkM9tEbjoca8QnrW1WqF53moKiKCyMOi7H48tpRSrVZ3\nOBmwDZjNZhlIujqdDqqaeb8X3Gw2KRQefwnDcGf8lPpcsIgwnU5zN6zb7WKMcQMbY1BV2u02AMVi\n8dkJyYC///iGfzJARJhMJrkA3/cJwzAffPL6lEqlQhAE9Hq9p9VsfbYT42RFEASICMvlMldxq9Vy\n9zhutVptr2LP85Ic54LTS4w3054wvXQnK758/cybwVtEhPl87hQ3p1T4pwNKpRKbzSaxwhiTqLYt\niPtRFLl5vF6vEREWi8XLHRC76vV65nCkfXdWbG/GPo/7/f7zcmxXo9FI1MUK009VdYtbuVx+kasp\nAUdRdHXz6fr8ENivn7/fZe681GRHwPG2HQGvAAN4gAJ/gXvgD3AL3G3H4fY7/wAc1bAz9NMAcQAA\nAABJRU5ErkJggg==\n""")
    def spreadsheet(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI\nWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QQWFA0J2YhE+gAAAk1JREFUOMuVkt9LU2EYxz9nm256\n1vxV4FmKlXEIUiGRLIoKlBEUeCGZFIHdSH9FY111GzTQm1KDCq0LQ3LQhRQUaHc5zWyUDPRITVtb\nS885O+/pYj/s1y58rr4v7/P9vN/3fV5peHj4yfr6ei+7q8vBYHAcgFAoZO+2QqGQXSC5CiISieSV\nhKZp+P0KAJqmoSj+vF5jYGDgjyhFgKZpSFIOIEm59c7eWsm7FAGKX8ErewGIxWL09PQAEI1GaWlt\nQbIl5qPzpQGGbpAhg4QEQCqVIi9Jf0+Rj1ca4HG7kb1eCq/j81UV/PiqdnRJwLau50/MtX6MPGf1\n7h22FhaJpzO5JrmCybZWvG3t/0ng8SDLMgD26D0+zc3RdOUiZZ0qwiGRFQLDFEgOD03Ppnh0vONl\n/+zb/iJA13UANh6MUbOyTMONPrLpJMn4KqYQGJaNs6oWUwisThXn0uqZEfXw7SLA7XYjyzKJyDT7\nr57nRzxWNJpC8KH+EJuGC1NkMSQL77F61KeTff8ksDe/YRlb6NaOWVLK2dPhJvy1C8PUUWu9CMvk\n6OhDj+PvBGZ1Dc59DeCrQRcWuiVwqpU0N6epz65xsnEvX1IpfCvvyXg828UEgUAgN43BQd7dH+Pg\n9V7qDhzBdrmoPl2HqHAQ7JB4/DlNY3yR9skJKlV1XAqHw1OJROLC77OtnZlBfvMa89wJyhqq8Zy1\n0Q1BZsNkekrQM/uKClV9cW1hIVDqfzDS3X1JX1q66U4mVefPTLltg5Blw6Uoywe7um6dGhqaAPgF\n9PUj6TDrLfkAAAAASUVORK5CYII=\n""")
    def graficos(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI\nWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1gELCzgrVaRReQAAAcRJREFUOMudkk9IFGEYxn/fzLTt\nEia07WGnUsiKXfsHSxkbgrelg50iRDaFILyJskJkXW3JbObgbbeku+apCIOILum5Dg1Iwkxh46HW\nUzM4fux0aI2NnGL9Lt/7vXzvw4/nfcRgcWBSSllmD0fTtLvi+sC18HFlDsexWxp2XZe5p08QxaHB\nShAEI3shiMViVQHw4OH9cPjGTTzPQ1UUBBD4PqGU7G9rAyFQVBVFURBCoOs60zNl7ty+J7QdtXQ6\njeM4fJmf5/DKCic7OkBKbNvG7enhWLFIHfj8dR1d139TKM1I3yyLi65LprOTuufhb25ySNvHqXfL\nvC//8rmr68SfRjY/apZFXVXxNzbYQvL6SoGF9Qyh3CL7tsJ5YG3tUzTB8UKBl4uLuL5P7dJRDuZt\njmg12j+8Idt3GoBMJhtNcCCZJD07y7OpKWoLr/ixvM13+wK5XI6+W5MEnsfqqkUqldpdIB6P093b\nS/fS0q5rSyQStCeT0QSW9fHfixdw9sy5aIF8/nLrcW7c1emZcqtprP73x9j46IhhPNoeGx9tPeqm\nafSbphE26tA0jf4IW/4eBJ4DlEoToqkfNsqrpdLEi53+T49VmPwrl5RfAAAAAElFTkSuQmCC\n""")
    def exporCsv(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA7ADsAOwdIxY2AAAACXBI\nWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QkPCjsE7Rz77AAAAZFJREFUOMuVk7+O2kAQxn+DVqIM\nzgMgCgo3SMdbRIqoUvAIuZrGDQdyB/QUNPScriNNJN6BlFTISAiwgysaaJgr1usYTnfRjTS7q9HO\nN9/8k8lk8nI4HH7wOWn3+/1nAMIw1M9KGIbqkIx7pGmawwuCCkgxptjjq+fdUDH33EQkuy0QgKoD\n0ze5mGIE54AIogW7ZAxU3geQIgPNDIIFEgf8EQPE5u7+i+XjfJX7olgpFVNQ0eyP5LeK1SSJefz5\nyG63ewdAHYcC40z/JjG9Xo8gCOh0Olyv17cAUuTnCioQJzFPT9Z5s9ng+z6r1YogCB5uaqDyr/8l\nBEVJ4iSPvN1uMcZQr9dJ05QoipZBEDTv5kARzYZIJHfe7/cYY/IZKZfL1Go1oihalu7baPutKMpo\nNGI4HGKMyfV0OuH7PlEUATRzAM/z8DyPSqVi9UuFarXKYDBgOp1ijOFyuQCwWCwAmrPZ7I+Mx+Nf\nx+Px+0erdz6fWa/XtFot5vM5jUbjd7fb/XbD/L/7224/AEsX2dlfAZgsvxGj7otLAAAAAElFTkSu\nQmCC\n""")
    def calculator(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABmJLR0QA/wD/AP+gvaeTAAAACXBI\nWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1gcEESQXWi6z8wAAAuVJREFUOMu1lUtrG1cUx3/3MdId\n62HZjjchwQQ3WJELlmvoC5xCSOm2lCSLZtEPUOgXaJb5Alkkm9BFKe2mGG8MpZvQRbc20mgytUWS\nXUIgkYVGzkOve7sYWXWJrCSEHDhcZjj3N+f8z5l74T2ZAPjm0tc/KKVuvCvMWvv9xu+btwA0gFLq\nxtVvvwPATIm3Br587gD49befbwL/gUcB3QPMVI7tnTtjAe32MzIZnxcvOiglMSbN2kcXkn2p7P9i\n9ThAHDfGgh/cf4hSkuZ+mzh+xqeff3hsFWPBZ86M37CwUEIIgXMOIQRCiDcD3/7pF86vf8YnH6++\nsb7bOwF3/vqbq5evHA9+8rTBxuYWG5tbbzdaYzKXRx++WF9nyveRUiY+LHeSZzMZzi4uTpYin8ux\nuHAaa+HkqVM8fvQIawfkpgu0W02ctfiZHEJKmvsNpBTgwDdmMvhefY9zxSWcc4RhyPLyMkopwjCk\nVCohpSSKIhyCtdUynufR6/WIomiyFJ1uF+fcqOsAg8EAEHQ6Hay1yR/mHEop3HAFQavVOj7jXH6a\najUAITgxP8/duxHWDijMzrFXr4NzFGZP4IBqtTqCTxdmJkvRjmPK5ZVEiiiiVDqH1pparcZquYyU\nkkqlitaalZWVUVVB+BopcBatNdZabL+PUgqtNVLK0RRIKYBEAs/zkFKCHXBwcHB8xlPZHJVKBRDM\nzc8T1GpopchkswRhiHAO4/t0O51kivJ5ms0m4CZL0e28pFgsAlCv1ykuLaGU4p/dPc5+sIjWmt3d\nXaRS5PN51HAdZ/LwTAbod3sYY0in03S7PVKpNMYYtJJorTHGJLIAcRzT7/eJ43jsGa8B7/BN2vcJ\nggCAwswMQZA0Km0MQa1GOpVKApXH9s4OSsrhVBSOgj2gpw/l2G80+OrLi6/MI/BKY15j+hBMq9W6\n9sefW9ff9WqKW/GPR/VIATlgFsgPvyiOaj/B3ND7QAzsA22g9y95DgxiphPiiAAAAABJRU5ErkJg\ngg==\n""")
    def textEditor(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI\nWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QkWEjcpO1ICSAAAActJREFUOMulk01oE0EUx38z3aNI\nFiIt4rHgKaBYKwEPghWEeOxF0LYnr6UXFTyKIMUg9SJ+gJoWijG9WxoRTVwQ7cFi040bTP3A1Wzr\nEBVakc14MEOzbWorvsv/Dcz7z29m3oP/DGGS4l36gBng2FZ6eIi8qZMAl0cvnQFmDh532I62ElhN\nvQHw7fk5tqNXT0rdrDstjdPeVEBZFVjdk6esCvzoethWX0xLBseKHOkfBhg3BMTjccSJpT+LfU1l\nTX3fJ39PMnTtGR+ejDO3EIRAh9V6H6UU9Xp9w0sHQYCbSa0Ve8t8LU11AD0RA9u2sW07Uuz7Pm4m\nxeBYkcXHGV6Vl1GlHEDPyGRj9q8E5uSBdIHFfIa5twpVyvFz/0XOn70wC4hNCbTWFNK9DFx5ijd9\nh8rn76j5B7zvGqazzTdGCLTWZLNZfslDzDsO7z7VWXo9Bb1pdq2sANo0oW5LEIYhuz+mefSlm/u5\nHN3yJTv7bpFMJnFdlzeVBYyLXE9QrVbxPI+RyQZHOyus7kgQHhglkUhgWRaWZUW6eANBLBZDa02t\nVkNrjZQSrTVCCIQQrdsbEQOlFI7jbDp1xmR9GIOJm7evn/qHKZ4wyW9aneiYeQn8EgAAAABJRU5E\nrkJggg==\n""")
    def plus(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI\nWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1gELEAARlER4oQAAANBJREFUOMvNkb0OwWAUhh/SxWC3\ncgfSuoHGYDZbO3RxB0TSxGQXsVoNJoOEG+hnN1osVmnip98xEIr6iwTvdvKdvPme58Cvk7j3YDk9\nHzCPo/K7FStuL/mg3PRcG8+1iRS9VfBSPi4w7jDHOZHIeHJiRJlb1SJbLSSAbXje91wbERA5WK93\nxubNDwBW65D5MkAEtBa0QLARwlDYaUFryGVS8QiAanQmFwjlUgGAwci/JlJP5VhOT4bThTT7M7ni\n//IZ89n0a2eMiaq1T7YVf5s9VHJLC4uyd44AAAAASUVORK5CYII=\n""")
    def minus(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI\nWXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1gELDzsiAFwSwgAAAIRJREFUOMvtkbEJg1AQhr8HadzA\nOivoCBkjrW1GCBkgC4itc8QFdIjUtiJE8+5PIcqzszOFHxwcB/93HAcH++PmJs3KGkg25pq6uKYA\np2CYPG8XRhMOGL1WCWkqB9zz17IoFNB9PO+2RwIzYYJ+EN6LrwkzOMfRShwKmkdebT7h+P4/8QOs\nUy3bRuSA2AAAAABJRU5ErkJggg==\n""")
    def refresh(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAABl0RVh0\nU29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMiSURBVDiNbVJNbFRlFD33e++V+a0zbQdb\nqLYKhhKmoaIzjX/RmEY3xGBYqLxEjJCB8LNhBxsMTQwRdGGi4AOjMUwlmDQBN/wEIZLUwqtx0dCS\n1NLGAUY7tB3ozLTz3vu+66LzkllwkpvcxT0nJ+dcYmb4SGWyzzTo2hEQ3vSkatWEmCfCuOPKEwAu\n2Jbp1t0eBHCCfIF0JrtF08RAT9cqfV1ns9HWFAGYUShWMDJ2v3xn+qEnFe+2LfNselc2w4zvAMSI\nmZHKZNcbuhjZ2tcdiseC0InQHA0gHNARDRkIGgIzxUUczw5XCsWKHQ019D4uVw1mNBEz49U9Z0/1\nrGv7NBgwxK3RHKquB0PX5JrVscW+9PPh3vWtpAmCEIRfrk2ot15sFwe+vuo4rmzRAYCZP7wzXRCu\np1gxLzLjM8eVZ8anZ5MT9+aPXu9o7tq3dVMoEQvh43e7RC0GAqAEAEipwlXH85IvPPuDlOoRgEHb\nMvO2ZV7549uPXhqdLOzdfewS7j8sYXqmDKkYAAMACyyvqumpSH9jJPBVZ/vKbgBTdWnruiZ2bnsn\n6XY+HUWicQU0Qb4D1mt38V8/37yAJ+O0J9VrF4cnq1ftqSXfvOOqAAD2W6gCMGoErpvfAOwE4D5B\nWLct854v4J0/+r4GEJgZF+1/1Knzf+WkVD22ZRbrWYezY6tK5aWO30fGbwCI6QBABBAR7v5XhiEY\nJwf/JABf1JNTmWyYiO72blx7Jj8zlwKgAagKABBEBAAdiRBWt4Tx5f63qa0lcuyVPT/fSmWy6ZrG\n9hWGrufyswfyheLrmkaubZmuWHZAeFxxcWFoij2P0b4yisM73gh90Jd8ubU5ci29a8A1dPGNVDI+\n92gBTY1B0oQYBAD/kaj/x6Glidzc5KXhyc7Mlk3hRCyI7rUJeq49HiqWXfw7W4LjeBQJGjh3ebTi\nSXUEAJYfSTFN5OZO3zy5LfmgsPBJ//c35o8P3CwN384jP1tG1ZUQRCjMl+S5y6OLUqmMbZljAOC3\n8BOA7bZlci0wA8B7DYa2VzFvkFLFDV2bIcJQ1ZGHbMv82w/3fy5VdmoTZczGAAAAAElFTkSuQmCC\n""")
    def folder(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz\nAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHCSURB\nVDiNpZAxa5NRFIafc+9XLCni4BC6FBycMnbrLpkcgtDVX6C70D/g4lZX/4coxLlgxFkpiiSSUGm/\nJiXfveee45AmNlhawXc53HvPee55X+l2u/yPqt3d3Tfu/viatwt3fzIYDI5uBJhZr9fr3TMzzAx3\nB+D09PR+v98/7HQ6z5fNOWdCCGU4HH6s67oAVDlnV1UmkwmllBUkhMD29nYHeLuEAkyn06qU8qqu\n64MrgIyqYmZrkHa73drc3KTVahFjJITAaDRiPB4/XFlQVVMtHH5IzJo/P4EA4MyB+erWPQB7++zs\n7ccYvlU5Z08pMW2cl88eIXLZeDUpXzsBkNQ5eP1+p0opmaoCTgzw6fjs6gLLsp58FB60t0DcK1Ul\n54yIEIMQ43Uj68pquDmCeJVztpwzuBNE2LgBoMVpslHMCUEAFgDVxQbzVAiA+aK5uGPmmDtZF3Vp\noUm2ArhqQaRiUjcMf81p1G60UEVhcjZfAFTVUkrgkS+jc06mDX9nvq4YhJ9nlxZExMwMEaHJRutO\ndWuIIsJFUoBSuTvHJ4YIfP46unV4qdlsjsBRZRtb/XfHd5+C8+P7+J8BIoxFwovfRxYhnhxjpzEA\nAAAASUVORK5CYII=\n""")
    def folderOpen(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz\nAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHuSURB\nVDiNpZM7T5RBFIafme/bXcNHsiFeEhsttTAhVtR2Flps4T8wsaMmxM6S+AsspIF/ocZQGC1MiMTE\nSoxIIrALGNjLnDPnWCyLLCgUnmSqOe9zLu9McHf+J8L8/PxLd3/4l7uuiDxaWFh4fy5gbm5ur9Vq\nNc0MM2PUUafTYWVl5VVVVQ9Gyevr6wAsLi4O/CixFBFXVba3t8k5j0FqtdpMu90+cHfcnaqqcHdm\nZ2c/AXdPAARVxczGINPT05NTU1NUVUVRFMQY6Xa7LC0t3Rl1VaqqqWZy/nNGABGh2+0SQiCEQIwR\ngJTS8eZLEfGU0hgg58yobXc/A1DV4yWWKSVTVXLOLH+M7PUiUDvXOqvu12aeLPdCjF9LVUVEyDmz\n24s8fXyPIoYjj4B/vJOkdunZi7e3SxExEcHMCDgTjYK1779wH+oJp3wHYgzcuDxBCFgpIqY6BBQx\nUMRADOGM8ERl+v1MvAqAH9k4XFpZFBQx0CjjGeFAjF7KZHMaRRyNaaWqWkqJgwE0J+ts7Q/op4z7\nsNpAM0ltbBVlEdja6w9HCCGYmfFlp871a012D4W+GL2kx6LTI8UQ2Ng5JIa4VbrD6ias/qxzq1nn\nzeoPsl38QzvtfbLb6zI3rrz7sFndBGft87cLhSdiA7PnvwHfolGj0Ct3mAAAAABJRU5ErkJggg==\n""")
    def about(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAABl0RVh0
        U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAM2SURBVDiNbZNbbFRlFIW/8//nWlEawIZO
        ofQ27YBOqVOCBU1TLkYt+qKihsSEmBgTKwZJTCdBjGmirRck8UENiRHS+OCDCaBHI4KO1aAFaRla
        24Jjp2KdoS1Qe5lpp3bO70NLA8Gd7JedvVfWXllLU0pxYxVvawkAzwB1QHB+3AVEgNa4G+67cV+7
        DlC8rUUAjYtyzFd3PrrOvifgE5Xl+QCcv5ik80LCO3Ts18xkeqYJeDvuhr0FgPnjtvuqikItLz3s
        nIoOcKI9Rk//MABrSvJ4oMbPxrWrCL//9dRPnQMdQG3cDXv6PJPGTetKQ2/uesjZs/9Lro2l2fvc
        Zir9+aSnZvihI06r28nxX2K8u+cR55UDbvWPHfFGoJmi+uZAcPt7qb+Hx9TT4U9VUX2zerHliMpm
        PdXTP6RGx9NKKaVOno6pmp0fqYa3vlCJkXEV3L4/XVTfHJC5/q0vv/Dkhk2j42nt0LGzABiGzmfH
        z3PYPUd79188vuVuVi7P5fPvexkZTVG6YgklK5bKU9E/JwRQV1Xh0060xwCwTJ1Ll8dIXk1hWwZV
        FT4Arv6TxjB0chyLzt+HCK0uEFKIOh0IBsuWE72YxDAkpmlgWQaWaRAKFLB7x0aUUhw82oFjWwih
        kbgyyeriPDylgtdFRAgNQ9cxjbm2TIO9z9Zi6pLDX0XpuzRKjmMihMCxTDQ0NEAAXV2xy4QCBRiG
        nGNh6Cy+3WYgOcaZ3gRt0UEc28SxLXIck/LCZcQGryGk6BJA5NyFhLdlfRm6LtF1iWHoaELwc/cg
        p3uTSCmxbWMBpNKfR/cfQ14260UE0PrxkTOZDWtXsf6ulehSoktB7iKH3U/dS8Nj1eQ4JpZlYtsm
        a4rvpMyXy4HWSEYp1SribrhvIpVp2vfBN1OvP7+ZUMCHlAIptQW/G/O6BAqX8ERtKa99+O30RCrT
        FHfDfTdZeWuNv/qNhgftaGyYaGyYxJVJbHvu58rSZZTkL6bp4Mlpt63n7My/s7VxN+zdEqY7brP3
        7dpxv11V4dPKC5eiaRrxxCi/9Y9473zyXWZ8crop63k3h+n/4iylqFNKBQGklF2zs9mIUuqWOP8H
        ZvdMlKLbimEAAAAASUVORK5CYII=
        """)
    def preferences(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
        WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QkaDBM5i2PCSAAAAfBJREFUOMulkktoE2EUhb+Z+EyK
        TRQKgkqwzMaFtt1FrC40FGJm60JwIVSkqLUtElICFQNDQqBrQXRlQIriwomN0GJXgtI2iUkXFYJV
        adOXhiBERDozbmaGMR3rwrP7ueece++5P/wnBOcjnVGigArI8Vgi9xdNNJ1RbI7YUlT7r/YDqKaZ
        q/j6tQHNbLQd6YxiNBp1I51RDPdaw6pFAcR0RolaZKur19vmZhwFePDwPvFYQgZyACKgDt4cMp4+
        mzAA9fatETbX15A6Jer1r/das4ndGRUsMYBgFW8MDBqatiXoum7oukZhfk4ovC8CyDsFK7R0sBHp
        u0i5UmG59gUgGY8l7v7zjE68yr80SpUS3Sd7KJYLmBNMArqrQTCSOgzUrPeVkE7XCYmjR47RbDZ5
        N/cWtzU8TvH4cJi+UCcdAS/ZmU2Ot39LLn1eOtd9qoeAP8BKbfnyhfD5+emp11XAABCDkVQXUHs0
        JjNbXmS2vEjHQR8A5t5yLv8CSZI4e7rX+mR2HiJQHB8OM/WmxJamI+7zs1Fv2iOaI8vZJ4850O7n
        TKgXYMxpAMDuXR72+A7x88cvsvkFgHCrSS6vUv1Y/SNsEWBl4zv7fQHa9np4PvMBIPxpcnTaSTRN
        kmvrqwtA0r5CMJK6BEw4uNvEO+E3N+LV9uq8VLwAAAAASUVORK5CYII=
        """)
    def stop(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
        WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QoRFy0Na8CcwAAAAsFJREFUOMttk7tPU2EYh59z6QVt
        jcbI4CWGxkAreGlquAmpNoiamJC4sRBY/A9cOjgYaRwcTByMC3HQwbsxuJhQJJqwiMHEDg4otdQW
        SmmhB+G05zufA6WC8iZfvuRNnt97+eVV2BKPwmE9PTHxRMBVdggNxgRcjkJlM6f8Az9r9PkuXbx2
        za1oGgBSShACaVl8ePjQ/DIz817AlShYNYEq/MLv8/VGhobc8+PjmPn8tupOr5f6jg4+PH1qJpLJ
        MQF9UbC0kVDIkZ2cfBk4dqw3Mji4Aa+ugmVtExCqylo6TSAS0Vfn5o4slUpnBsPh51pnJvPmeGNj
        z/mBAXc2Hseqr0ePxSCZRGazG7OfOMHeu3epJBIYX79yPBzWjVTq6I9EIqj1qOrj/uvX9cy7d5QL
        BdS+PtSWFpSODvj+HXX/fvYMD+Patw9FSkrj4/wuFGgOh/Wpz58DuqIoICXlQmGj1ZERcLlw9fbi
        vnEDXVFwejyY8Tj5O3ewgXXDQAqBAqj/eSUl4v595NQUzl27cHq9WNPT5GIxhG1jAzYgqztSd/S7
        uRl3KISu6zgcDnYHg9SFQsgqLMplxNzcXwEpRA1WW1rw3rqF0+tlPR5ndXQUp8eD7949PO3tmLkc
        xrdvyJUVAHQp5YaaYSAsi7q2NlxVeHF4GNs00YAD/f3UnTrF+oMHoGnY1aLaBSm7K8Xi4UBbm1ZK
        JCi9fk3l508Wbt6knMlQXlwk9+oVa7OzJG/fRtE0fH4/6aUl+8fycl6JgVODtycbGrpbg0FXKh5n
        rVisLWvrUxwOGpqaSBcK4mM6vWBDpzYGIgJPcsVil2kYhwKtrXppfp6KaW6DVYeDBr+f2XxeTP76
        lbKhPQqp2jFtduI/eLD77OnTLkUIbMtCWlbtTyST1qdsdsaGrigsbrvGrSICenayV4VpG85FYXkz
        9wfHTVL214b3FAAAAABJRU5ErkJggg==
        """)
    def find(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA8ADwAO80BmcbAAAACXBI
        WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QsFEA8FJf2tLwAAAfZJREFUOMudkk1rE1EYhZ87ySRN
        mmaGSlIKCrVdaBpFFMGFuBQKVXfiJr/Ab6n0H4i2JEFEFHRZd1UQxU2oO0HsolQopIlWq5ZQNY3N
        RydNMjPXRUhJQlKqZ3cP7z3v4bxHPHn6eDH3J3eMPUBV1ecTtyYvtpDT0buW3CPuTd+R7aJOKetc
        Pr+563ZN0zvyTiHEziOZTHYcCoVCXYV3HLQPZjIZZl/MApCYSwDQtGt3B9++r5JKpzl6aoxtxYtp
        K7hkhdT8ayZu34zEovefNf4o7Q40XSOVTnPo5BifC14GBwKMHAhSEj600XH8mj5z7caV410dJOYS
        DIdPs1Jwc+nMEL4eFdO2UR0K75YlwSPjNktvFgABoHQKS3oDDA3oWLZk2zSp1CzKVYt+n5tfZbUl
        CUVKiZR2SzButwuEoFy1qNYkm1s13KqD/f0epBAtXXACtmmaLU5sY4M1o4rfo6L3ubAtid/j5NNG
        gX09lp1rcq7UK+pC03Q0TefCufOkF94S7BN8+ZknmyuRNyp8XFmnVK6QW3rlLBWLPxoCIhqfmrEs
        K9J8DcMwcDhUTpyNsLxWZMtUGOyVrC++ZPjgCAAf5t+nHj54dFh0a9jV65enAoHgZDPn6/URHg3z
        O5ut92X1K4J/RCwelQ2R/xIAlFg8agGUDYO/Boz2038z5y4AAAAASUVORK5CYII=
        """)
    def findr(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
        WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1gEGFgQD9XZoggAAApVJREFUOMutk01sDGEYx38zs7O1
        SLfMLMGBVtCJ4KCJg6C4NHEgUkmJr2NLilpBpEQQgooica1EE8Q2EtGDS320REiJj52lRWJbldRu
        d2c/ul27O68DO2kvTv7Jkzzvm/x/eZ43/1dinPYdaNQ0TYsUz9FoVL/aei3KPyQVG/+hA2tLvWVd
        S1bUiBRTJVWMib6XD6SEFV93qaX10T8Bjfv3arruiyysqmEg7WHl4lmY4RjpZAIr1InLpaAosmNS
        VTXgbzq8BcAFoOu+SPnilXyxSqhbXc4kt4KqyHSHBDOWbGD4fSfHjjY7gPMXz9YWe5dzO9nHvOml
        FGxBNlcgm7PxlZbwdWgMCbCsOABebxklb45zeassgB3OXGohweBwgnAkQzydZ47mwS0X0KfYAIRC
        IQBatynsutJDde1+gJsyQMKKr+t73cXMUglzYISR1BgvzO/EUhmi7++zaeMmDMOgrUFj99VnDD5t
        5505WACQAaaVTe+qKJ9P+NU9Knwl9IR+khzNMvy6A13TGE2POuaBJzd51x9lxOxQgCrpzJlTYu68
        cny6TtAMkkqnnGdZtnQZ1WuqaWvQ2Hmpm3BPO28/RYmZAYCqplt2rwtwzAeb/FhW3NkX+GNueUr/
        wzY+fk8SMwP8WlTPkZPXewFJbm4+IQXNIPnCL7toMgwDwzCorKzkm7yC4PPn9A9ZxIJ3qTv9Atsz
        28mQDOA/eEgCEMJhIITgxh6dzz+i3AkEiHzoYFV9B5O0BeRyuWIEhDwulXY+n58AaLpls37mZ2o2
        72Z5w2PE5Dkkk0lyuTyAMjFIgKq68XrdDiCTyZBIJMhmsyiKgqqqf8sFYE8AKIpy+0LLue1CiAlT
        FEuSnH+Hx+NpB3L8D/0Gec0bDM69rVkAAAAASUVORK5CYII=
        """)
    def runIcon(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
        WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QwGESQhztmtXgAAAiFJREFUOMudk0trEwEUhc88Mskk
        TSYxmWliExNaSTAjukrR1EhSbIoFwWd0J1gQwUK23fkHXPQXSJeCL7pyo4ggLgxCTRWxWGygEUr6
        0KQzTTIzuS7EpmIpsXd17uaDc+85QHd4HGC4XToCwAGgCYB6BbC7l/z42OtgMJgG4OsVwPwRiiwf
        GT6V+sYwTMeyzC/lD59utlqtz7VaTe/JQjQWk7w+qfjs6RzvkTz+anVlsr9fGekw9GYgNFCv1Wq0
        LyCpqpIoOorXCzfYSGSAnTg/wfW53eGN9fXbolNMOkXXu2TyWGN5ubI3YDiVkjiOKV69co0FAa4+
        N9SkyqVPpwWXU0z8qP+cNC1rdWhwqLK0tNT8B5DLZqW22S5euniZ3dLrMIw2DKMNu8OOeCLB5fPj
        DiK6QDBTiXj8feZMplEqlcyd3wdkBQ2tDgDQdA0gAgGw8TZ4PT7opIPIYvyH/IbXE5B4jnUDaO4A
        FEVG9ftvf7q+BZvNjsPBMCzTxOzsA2vx6+JmLBa9owRCbwFauzs1ZfyVPlmWySYIAAjR8CB4nsfj
        J4+shY8LRjxx9F5mJPuw0+msFgqFFvaKrywrEAQbdYjw8tULKpfnLbfH8zx7dnRaEOyVXC6r7fXG
        LkAJQBTtNDNz39J0bWU0O3orIIfmj6vqxn5B6t4gIGN7u7V5biw1fUI9OQcwm4qiUM9RJqIwAAPA
        GsMw1n/XkojYg9T5FzBGwR9B4E5iAAAAAElFTkSuQmCC
        """)
    def documentNew(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/ADpAE8017ENAAAACXBI
        WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH1QISDiYc07YZKQAAAWpJREFUOMutkE9LW1EQxX9z741W
        JH0lgtDKWxbc1O5cZqkb8w2ycVm/Rd6y3XcjBMSC38BNN90qhVJKslJKSVqEEP9FYpved8eFJsYY
        k1R6NjMMc+acM1Iul7drtVqREZid/cvcXJtn0W/yy5/f5aJvH+HPvmTDGaVSScfh/HhTL0/faOe8
        oJcnK52LxuKutrLr2jIzrqvSbDYJIQAgIj31jNlj2n4h474iZgnrTCbY9mrHt1tTzld7BwbJ3Wrk
        CGvqiHmFuAJgMSpG01+L4F66/qyD5OtebzoLTIE4EAuCABduNFkIOk/Q59hQRdNpQNC0ot6besam
        FffQ57uHAq/x4SfgsVoBFO9f6OlZ69PM/PeDkRFEBOUpHV1DdYE0/QE8YWvn0GxsbL8FcKPItzWL
        1zwiQhRFNBpJT9QwIfp/0497EYY5eIh8x8GwpcHZsB0zqd2xEXK5HI+Bi+P4Q5IkxX8hxXH8nv+F
        K8w9mWB7rBTJAAAAAElFTkSuQmCC
        """)
    
    def logo16(self):
        return IconFromBitmap(self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
        WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3AYYEC0yRx5UOwAAAB1pVFh0Q29tbWVudAAAAAAAQ3Jl
        YXRlZCB3aXRoIEdJTVBkLmUHAAADL0lEQVQ4y22TbUiddRjGf/dzznnMOnMoHinMcxTfX4a4ZNrC
        toGrD6tBg6wkasig6OOKZHPRjLI+5CiCYl/WYLH1Mvowg1hSS3Isk8nMl1labB4beo5vs+f/dM7z
        cv59sERa97f7vq/r9+m6hP/Mz5NTZb7vvxw0Q3uSiWQZQCQSmXFc95IZCPRuq6ma2ayXzcvQyLWz
        yUTymSuDV7TnByRaWgMIs79PEAr4uumhByUSyT/X/EBD+x2AwaHh6eEfh0s9HZZo5SP4mRD636fW
        BMQjPtNPUP7UjTsaf2tp3lG+Afh2YPCzsdGxJ8N59aLNinXPJjMYaDKAYLjT2KujunZb7Retu1qe
        ku8GBssSyeT0rXmfQHjPulEL6H8gsk7TGkQ0GkH++p57C4SCSKQ8eHttrTN+I67JeVq81DIPV7/O
        8qpJQf4ikzcfI77Uhucl2NfUyUIij7xcj4HxN7k116ezsszOoJN2WkPZ+ZJYDXKg5QhfXT6K45eA
        hsroSSwleF6a8wOnEaCu5DQV931OfKFInLTTati2igXMmLaVkLtlnuRSMbYCZcPI1AsoBel0FNte
        v92cr8UMrWKEotq27Zjhuh4QFMsSvhnq4LVDrVQUf4qyfCxLULaBUoKlBGUJuxvOMvJrC2RC4noe
        huM4c+G7b2MrzQ/DT3D43X4m4tW82H6Ql9oOoiyNUmAriMW+5sZSIRO/NJMTXsNJpeYMJ+VcNPSS
        FvGxbEFZQeLTDbzxwRkqi66jlGArwc1KsKuxj3NfvoqIj7CoXdftN2LF0fcSiaTs3jmrm3aeRymN
        ssFSGVLOXSgFOfkztD/6Ed29H6Is2NsS1wvzCxKLFp0QgJ53ei8UFhXuy86ZNUoKL7Ps5HOPpzj2
        fi+ptS0823aSmtIxJKDJysqgMtn8dKmqr+vIK/s3otx1rHu2qqa60DfqjVOfRFhZCW6kSAO5Wz0O
        Pb9IIDOamRyf+KPnrePRO8p0tOv4hZBpPr69cbvODpfL9akAWoTqKp+0Na2vDl8VJ53ue7une///
        thHg41Nn6q6Njh12XGdvXl7u/QArSytzIdPsr6+vO9HR8dz4Zv3fVDCAyQsMbqMAAAAASUVORK5C
        YII=
        """))
    
    def logo64(self):
        return IconFromBitmap(self.__conversion__("""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
        qll7sbFlTs8FXLzuElpbW3DWVkqaEXw56/hEwPBIyPBwyPBowOhYSLmUlNtnlPa2mI52S0dHTEd7
        THurJZPRKtp0SYnb+NgY27duo6/vKGEYVDMKIkauuebK21/9l6/88Av+0tSu3U9v/MUvfvVIX/9R
        DYNAKjzO2ti/3LRmFTNnz0Kd86+zNBS9eaZnXcIIEYxRr0ZXrhGp8gFJ6OzJ4yfZvXMXJ4+dwISB
        L0pXJLZWe3oukJded+01a9Zc+Oh/6GtzP/jhg3dv3brtrflCXo0xlTwmNrZks1l65vewZOkSOru6
        CFOhR41OG4hMjcbUvUYbGOI4ZnBgiIPPHqD3cC/FYrH2MpZndtrUlJP1l17ynRtvvOFt/2kvTqrq
        zK9//Y5vHHzu8PWFfN6JMUakJlLENsYEhra2NqZNm8bUrk7a29rINWVJpdMAROUy+UKR8dExhgaH
        OHP6DOPj41hrCYIgqRTVZOVY19SUM4sXLXzo5ptveo+InPyzeHVWVafdcce3v9zff/R1J0+dklSY
        rrxBqnXlQD4row5cXdI9uVCMqdUI+bu0wofLUSQzZ87QuXMv+OG7bnr7LSJy5s/25ektWx7/2JNb
        f/fq8bGJDcdPnAgEIQiMIpW1IY2vTT+vO05t7ERRZs+aZVtaW7Zcftm6H2/YcMWt/1+8PV7/7/Sp
        069/4MF/Xjo4OLQwlU5dIrB6ZGSUyYkJylFUfeGpuaWZKVOmoKq7ozja1tXZeeiG17zq2ekzpt//
        Qvbv/wGeTVTTDVh63gAAAABJRU5ErkJggg==
        """))
    def backward(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAAK
        T2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AU
        kSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaKOg6OIisr74Xuja9a89+bN/rXX
        Pues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgAB
        eNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAt
        AGAnf+bTAICd+Jl7AQBblCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3
        AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dX
        Lh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+
        5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk
        5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd
        0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA
        4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzA
        BhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/ph
        CJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5
        h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+
        Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhM
        WE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQ
        AkmxpFTSEtJG0m5SI+ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+Io
        UspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdp
        r+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZ
        D5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61Mb
        U2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY
        /R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllir
        SKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79u
        p+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6Vh
        lWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1
        mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lO
        k06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7Ry
        FDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3I
        veRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+B
        Z7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/
        0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5p
        DoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5q
        PNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIs
        OpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5
        hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQ
        rAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9
        rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1d
        T1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aX
        Dm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7
        vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3S
        PVRSj9Yr60cOxx++/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKa
        RptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO
        32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21
        e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfV
        P1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i
        /suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8
        IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADq
        YAAAOpgAABdvkl/FRgAAAdFJREFUeNqUk0toE1EUhr9z5+ZlRdPWPlxp0WTTpihqK+rCrUF3LlwJ
        xnSt6+k6Wdd1Rym4FkSidFtBUbciRRQUH0ioqDTFJPO442ImmpaJ1bu53HPP//Of858j9x6F7HZs
        h6oortUqnN35p3cB7hVhZWyY8sZ3ckk56i/gEsKr2SKXLp5LBg9UYDsspFMsnT9JbjSPiAxWqZMk
        T45SPnOcnGvgwzcojIMoOrbD9oYJTb1DcqNU4GDxEKlmCzoeKAUmhKtlsr3cEAhDuPuQCd2TnM1w
        a36W7NAQ8nYjAlkKVAjrX0AEpA9cnIhLWLzD7fERrpyYJrfZhTdNsDRoKwJ5IbgudFzw/CiW1jB1
        oK8HxoAXgBtAF8BAYMA3YOK3CSAIopsubLZjG2sVrn/9wc21F7QJCKfGItpQg85COgM6A1YarBQo
        a7sL0ptE26EkisaRw0wWjpL+1IaWF9V8bATCWIUJwPgRePVxH8FvGxUr+X1cmJ9jT1vD5xbM7IcH
        q3SM/8eJno2StAu2w4LWLJ2aI5cfRjIC9xtQryL/NMr1Ksu+z+nnz/j4ep2u7w2exIG7UK/y0him
        372nsfaEn/9NEJNs1Spcbm1xQxRPk3J+DQBnP6UBYL92HAAAAABJRU5ErkJggg==
        """)
    def forward(self):
        return self.__conversion__("""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
        """)
    def refresh(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAABl0RVh0
        U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMiSURBVDiNbVJNbFRlFD33e++V+a0zbQdb
        qLYKhhKmoaIzjX/RmEY3xGBYqLxEjJCB8LNhBxsMTQwRdGGi4AOjMUwlmDQBN/wEIZLUwqtx0dCS
        1NLGAUY7tB3ozLTz3vu+66LzkllwkpvcxT0nJ+dcYmb4SGWyzzTo2hEQ3vSkatWEmCfCuOPKEwAu
        2Jbp1t0eBHCCfIF0JrtF08RAT9cqfV1ns9HWFAGYUShWMDJ2v3xn+qEnFe+2LfNselc2w4zvAMSI
        mZHKZNcbuhjZ2tcdiseC0InQHA0gHNARDRkIGgIzxUUczw5XCsWKHQ019D4uVw1mNBEz49U9Z0/1
        rGv7NBgwxK3RHKquB0PX5JrVscW+9PPh3vWtpAmCEIRfrk2ot15sFwe+vuo4rmzRAYCZP7wzXRCu
        p1gxLzLjM8eVZ8anZ5MT9+aPXu9o7tq3dVMoEQvh43e7RC0GAqAEAEipwlXH85IvPPuDlOoRgEHb
        MvO2ZV7549uPXhqdLOzdfewS7j8sYXqmDKkYAAMACyyvqumpSH9jJPBVZ/vKbgBTdWnruiZ2bnsn
        6XY+HUWicQU0Qb4D1mt38V8/37yAJ+O0J9VrF4cnq1ftqSXfvOOqAAD2W6gCMGoErpvfAOwE4D5B
        WLct854v4J0/+r4GEJgZF+1/1Knzf+WkVD22ZRbrWYezY6tK5aWO30fGbwCI6QBABBAR7v5XhiEY
        Jwf/JABf1JNTmWyYiO72blx7Jj8zlwKgAagKABBEBAAdiRBWt4Tx5f63qa0lcuyVPT/fSmWy6ZrG
        9hWGrufyswfyheLrmkaubZmuWHZAeFxxcWFoij2P0b4yisM73gh90Jd8ubU5ci29a8A1dPGNVDI+
        92gBTY1B0oQYBAD/kaj/x6Glidzc5KXhyc7Mlk3hRCyI7rUJeq49HiqWXfw7W4LjeBQJGjh3ebTi
        SXUEAJYfSTFN5OZO3zy5LfmgsPBJ//c35o8P3CwN384jP1tG1ZUQRCjMl+S5y6OLUqmMbZljAOC3
        8BOA7bZlci0wA8B7DYa2VzFvkFLFDV2bIcJQ1ZGHbMv82w/3fy5VdmoTZczGAAAAAElFTkSuQmCC
        """)
    def goHome(self):
        return self.__conversion__("""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI
        WXMAAA3XAAAN1wFCKJt4AAAAB3RJTUUH1QoOFCUTUyrSOwAAAetJREFUOMuVk79rU1EUgL97+95L
        00DyJKBVh2RRexNoVawRXByMQhOnh9RKJ5GioxhcOrRuwan+GOrUJYv1x2AT8A/wPxB5W1zEWtvw
        YlGJIXnXIfbZl1AhZ7pczvfdcw7nwgHhKVWsgK6A9pR6yDCxB3tKaU+pPUlxaHixOKPLN2/8VyL6
        4ZrrbhSUYv3cWbYnTnHk8DgnvCZTa2vUXJeCUtcOuW51QLAfflOcYff4MZTKMhaN0mq1GNv8SrZc
        HpCIfrh6+xadZJJ0Kk0qlQJAa2i32+zW65wslUISsR9+96BExzDJ5S5g23bQmtYaAN/3+bm1RXJu
        LpCICuiCUrx/VMZrNjk/nSMejyOECAl83w/OhhCM5vPUXBcDuAOsTp0+w/3SPTaqbwPwycozVh4/
        RYsRdKeFMEbR3d8sLy3R7qXMynl4vjCZIRFPAKDUBJmMIpvN9F4UkpH0ld7EU3mQFlprFiYzzMO6
        7O/TsixM08QwjOD+S+MHAB/qO3S7fpALMCCQUiKlxJKfAehg8fFTA4Bv3i86IhJaJGNgs/4Oz+co
        AJcuTnM1GkPqcS5Lk+1NQhUY/RX8m37vpe/eDqLZOHD1A0EkEsG2bRKJBAKJEBCLxXAcZwCyLCv8
        F67POq8Ah+Fi9eWL13f/AFb41aOFu4AaAAAAAElFTkSuQmCC
        """)
    
if __name__ == '__main__':
    imagen = imageEmbed()
    path = 'f:\\salstat src\\icons\\go-home.png'
    imagen.convertFromfile(path, True)