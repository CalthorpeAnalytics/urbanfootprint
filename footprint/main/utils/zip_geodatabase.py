
# UrbanFootprint v1.5
# Copyright (C) 2016 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.


'''Script: Sample_Zip_Geodatabase.py

Purpose: The purpose of this script is to show the basics of using python to zip up an ESRI file geodatabase.
The

Original Post: http://nodedangles.wordpress.com/2011/02/08/zipping-a-file-geodatabase-using-python/
'''

import os
import zipfile
import glob


def zip_file_gdb(path_to_file_gdb, path_to_zip=None, overwrite=True):
    if not (os.path.exists(path_to_file_gdb)):
        return False

    if not path_to_zip:
        path_to_zip = path_to_file_gdb + ".zip"

    if os.path.exists(path_to_zip):
        if overwrite:
            os.remove(path_to_zip)
        else:
            raise Exception(path_to_zip + " exists, and you specified overwrite=False")


    zipobj = zipfile.ZipFile(path_to_zip, 'w')

    for infile in glob.glob(path_to_file_gdb+"/*"):
        zipobj.write(infile, os.path.basename(path_to_file_gdb)+"/"+os.path.basename(infile), zipfile.ZIP_DEFLATED)
        print ("Zipping: "+infile)

    zipobj.close()

    return path_to_zip
