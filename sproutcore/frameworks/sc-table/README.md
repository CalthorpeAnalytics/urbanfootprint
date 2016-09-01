#Overview

This is a table view for [Sproutcore](http://www.github.com/sproutcore/sproutcore).

Design Goals:

  * Use the existing Sproutcore API -- no modifications to Sproutcore are necessary.
  * Be intuitive and responsive from a user's perspective.  (Includes rendering quickly, so the row view rendering is kept intentionally simple.)
  * Be easy to plug in from a developer's perspective.

Current Limitations:

  * Currently unstyled (hopefully it will get a good default theme soon!)
  * Currently read-only, with plans to add a row-editing mode.
  * It's fast, but I haven't put a whole lot of effort into making it as fast as it could be yet.

#Dependencies

  * [__Sproutcore__](http://www.github.com/sproutcore/sproutcore) (Versions 1.4-stable through 1.8.0, though styling is currently a bit off due to Sproutcore theme changes I haven't caught up to yet.)
  
#Demo App

Check out a demo app project here [http://www.github.com/jslewis/sctable-demo](http://www.github.com/jslewis/sctable-demo).
And a build you can play with here [http://jslewis.github.com/sctable-demo/index.html](http://jslewis.github.com/sctable-demo/index.html).

#How to Use

The main view provided by this project is SCTable.TableView (in views/table.js).

* __Row content__: Bind an array or ArrayController full of your row objects (any SC.Object instances) to the 'content' property.
* __Row Selection__: The 'selection' property gives you an SC.SelectionSet of selected rows.
* __Column Definitions__: Bind an array or ArrayController full of column descriptor objects (any SC.Object instances mixing in SCTable.Column) to the 'columns' property.  The order of these objects determines the order the columns are shown in the table.
* __Column Selection__: You can select one or more columns - if you do, an SC.SelectionSet at the 'columnSelection' property will match it.

The table view header subclasses SC.CollectionView, and the table body subclasses SC.ListView, so both your content and columns array controllers can have full collection view delegate power if you wish to implement it.
