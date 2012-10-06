'''custom grid cell renderers

copyright:  2012  Sebastian Lopez Buritica'''
__all__= ['floatRendererSub', 'floatRenderer', 'AutoWrapStringRenderer']

import wx
import wx.grid as Grid
from wx.lib import wordwrap


from slbTools import isnumeric

class floatRendererSub(Grid.PyGridCellRenderer):
    def __init__(self, decimalPoints, color= 'blue',
                 font= "ARIAL", fontsize=8):
        """
        (decimalPoints, color, font, fontsize) -> set of a factory to generate
        renderers when called.
        func = MegaFontRenderFactory(decimalPoints, color, font, fontsize)
        renderer = func(table)
        """
        self.decimalPoints= decimalPoints
        self.color = color
        self.font = font
        self.fontsize = fontsize

    def __call__(self, table):
        return floatRendererSub(table, self.decimalPoints, self.color, self.font, self.fontsize)

class floatRenderer(Grid.PyGridCellRenderer):
    def __init__(self, decimalPoints):
        """Render data in the specified color and font and fontsize"""
        Grid.PyGridCellRenderer.__init__(self)
        self.decimalPoints= decimalPoints
        
    @property
    def decimalPoints( self):
        return self._decimalPoints
    @decimalPoints.setter
    def decimalPoints( self, dp):
        if not isnumeric( dp):
            raise TypeError('the selected decimal point must be numerical')
        
        if dp < 0:
            raise StandardError('Only allowed values bigger than zero you input %f'%dp)
        
        dp= int( dp)
        self._decimalPoints= dp
    
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        # Here we draw text in a grid cell using various fonts
        # and colors.  We have to set the clipping region on
        # the grid's DC, otherwise the text will spill over
        # to the next cell
        dc.SetClippingRect(rect)
        dc.SetFont( attr.GetFont() )
        hAlign, vAlign = attr.GetAlignment()     
        if isSelected: 
            bg = grid.GetSelectionBackground() 
            fg = grid.GetSelectionForeground() 
        else: 
            bg = attr.GetBackgroundColour()
            fg = attr.GetTextColour() 
        dc.SetTextBackground(bg) 
        dc.SetTextForeground(fg)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        
        text= grid.GetCellValue(row, col)
        try:
            dp= wx.GetApp().DECIMAL_POINT
        except AttributeError:
            dp= '.'
        try:
            text= float( text.replace( dp,'.'))
            text= round( text, self.decimalPoints)
            text= str( text)
            text= text.replace( '.', dp)
        except:
            pass # allowing the non numerical values

        dc.DrawText( text, rect.x+1, rect.y+1)

        width, height= dc.GetTextExtent( text)
        if width > rect.width-2:
            width, height = dc.GetTextExtent( u'\u2026')
            x = rect.x+1 + rect.width-2 - width
            dc.DrawRectangle( x, rect.y+1, width+1, height)
            dc.DrawText( u'\u2026', x, rect.y+1)
            
        dc.DestroyClippingRegion()

    def Clone(self):
        return floatRenderer()

class AutoWrapStringRenderer(wx.grid.PyGridCellRenderer):   
    def __init__(self): 
        wx.grid.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        text= grid.GetCellValue( row, col)
        dc.SetFont( attr.GetFont() ) 
        text= wordwrap.wordwrap( text, grid.GetColSize(col), dc,
                                 breakLongWords = False)
        hAlign, vAlign = attr.GetAlignment()     
        if isSelected: 
            bg= grid.GetSelectionBackground() 
            fg= grid.GetSelectionForeground() 
        else: 
            bg= attr.GetBackgroundColour()
            fg= attr.GetTextColour() 
        dc.SetTextBackground( bg) 
        dc.SetTextForeground( fg)
        dc.SetBrush( wx.Brush(bg, wx.SOLID))
        dc.SetPen( wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect( rect)            
        grid.DrawTextRectangle( dc, text, rect, hAlign, vAlign)

    def GetBestSize( self, grid, attr, dc, row, col): 
        text= grid.GetCellValue( row, col)
        dc.SetFont( attr.GetFont())
        text= wordwrap.wordwrap( text, grid.GetColSize(col), dc,
                                 breakLongWords = False)
        w, h, lineHeight= dc.GetMultiLineTextExtent( text)
        return wx.Size( w, h)        

    def Clone(self): 
        return AutoWrapStringRenderer()
