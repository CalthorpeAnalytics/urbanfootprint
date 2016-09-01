
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

import os
import sys
import json
import glob
import urllib
import urllib2
import zipfile
import tempfile
import mimetools
import mimetypes
from urlparse import urlparse, urlunparse
from cStringIO import StringIO
import ssl

import arcpy

ARC_TOOL_VERSION = '1.0.0'

MAX_UPLOAD_FILE_SIZE = 104857600  # 100 MB

ssl_context_kwarg = {}
if sys.version_info >= (2, 7, 9):
    # TODO: _create_unverified_context() is a temporary no-op verification
    # and this should be replaced after determining how to allow Arc's
    # python installation to use SSL
    ssl_context_kwarg['context'] = ssl._create_unverified_context()


class Toolbox(object):

    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""

        self.label = "UrbanFootprint_Upload_Toolbox"
        self.alias = ""
        # List of tool classes associated with this toolbox
        self.tools = [UrbanFootprint_Upload]


class UrbanFootprint_Upload(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""

        self.label = "Upload"
        self.description = "Upload your Arcmap layer directly to UrbanFootprint"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        arc_version_parts = [int(x) for x in arcpy.GetInstallInfo()['Version'].split('.')]
        use_protected_password_field = False

        if len(arc_version_parts) == 3:
            major = arc_version_parts[0]
            minor = arc_version_parts[1]
            release = arc_version_parts[2]

            if major > 10:
                use_protected_password_field = True

            elif major == 10:
                if minor > 2:
                    use_protected_password_field = True

                elif minor == 2 and release >= 1:
                    use_protected_password_field = True

        elif len(arc_version_parts) == 2:
            major = arc_version_parts[0]
            minor = arc_version_parts[1]

            if major > 10:
                use_protected_password_field = True

            elif major == 10 and minor >= 3:
                use_protected_password_field = True

        if use_protected_password_field:
            password = arcpy.Parameter(
                displayName="Password",
                name="in_password",
                datatype="GPStringHidden",
                parameterType="Required",
                direction="Input"
            )

        # create a password field for arc versions less than 10.2.1
        # because they do not support GPStringHidden
        else:
            password = arcpy.Parameter(
                displayName="Password",
                name="in_password",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
            )

        email = arcpy.Parameter(
            displayName="Email",
            name="in_email",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        server_url = arcpy.Parameter(
            displayName="Server URL",
            name="in_server_url",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        project = arcpy.Parameter(
            displayName="Project Name",
            name="in_project_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        layer = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        return [email, password, server_url, project, layer]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""

        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        return

    def execute(self, parameters, messages):
        """
        The main entry point this file. This method is run when the clicks the 'OK'
        button from the arc tool UI.
        """

        messages.addMessage("Arc Tool Version: {}".format(ARC_TOOL_VERSION))
        email = parameters[0].valueAsText
        password = parameters[1].valueAsText
        server_url = parameters[2].valueAsText
        # remove paths and params from url
        parsed = urlparse(server_url)
        server_url = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))

        config_entity_name = parameters[3].valueAsText

        # layer is sometimes just the name of the layer
        # or a full filepath
        layer = parameters[4].valueAsText

        file_extension = get_file_extension(layer)

        input_filepath = get_input_filepath(layer)

        temp_dir = tempfile.mkdtemp()

        output_filepath = os.path.join(temp_dir, '{}.zip'.format(os.path.basename(input_filepath)))

        with zipfile.ZipFile(output_filepath, 'a', allowZip64=True) as z:
            if file_extension == 'shp':
                files_to_include = "{}*".format(os.path.splitext(input_filepath)[0])
            else:
                # this is a gdb dataset, in which case the files
                # are nested inside .gdb/ directory
                files_to_include = "{}*/*".format(os.path.dirname(input_filepath))

            for file in glob.glob(files_to_include):
                if not file.endswith('.zip') and not file.endswith('.lock'):
                    z.write(
                        file,
                        os.path.join(os.path.basename(os.path.dirname(file)), os.path.basename(file))
                    )

        login_results = login(email, password, server_url)
        username, api_key = login_results
        messages.addMessage("Login successful")

        config_entity_id = get_config_entity_id(username, api_key, config_entity_name, server_url)

        if not config_entity_id:
            raise arcpy.ExecuteError("'{}' is not a valid project name. Please try again.".format(config_entity_name))
        else:
            messages.addMessage("Valid Project Name: {}".format(config_entity_name))

        form = MultiPartForm()
        form.add_file(
            'files[]',
            os.path.basename(input_filepath),
            fileHandle=StringIO(open(output_filepath, 'rb').read())
        )

        request = urllib2.Request(
            '{}/footprint/upload/?{}'.format(
                server_url,
                urllib.urlencode({
                    'username': username,
                    'api_key': api_key,
                    'config_entity__id': config_entity_id,
                    'file_name': os.path.basename(input_filepath)
                })
            )
        )

        request.add_header('User-agent', 'UrbanFootprint Arc Tool (www.urbanfootprint.net)')
        body = form.get_body()

        body_size = len(body)

        if body_size > MAX_UPLOAD_FILE_SIZE:
            raise arcpy.ExecuteError(
                "The maximum file size for upload is {0:.3f} MB and the file you attempted to upload is {1:.3f} MB".format(
                    MAX_UPLOAD_FILE_SIZE / 1000000., body_size / 1000000.
                )
            )
            return

        request.add_header('Content-type', form.get_content_type())
        request.add_header('Content-length', body_size)
        request.add_data(body)
        urllib2.urlopen(request, **ssl_context_kwarg)


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.files = []
        self.boundary = mimetools.choose_boundary()

    def get_content_type(self):
        return 'multipart/form-data; boundary={}'.format(self.boundary)

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))

    def get_body(self):
        """Return a string representing the form data, including attached files."""

        # Build a list of "lines" of the request.  Each
        # part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary

        # Add the files to upload
        for field_name, filename, content_type, body in self.files:
            parts.extend([
                part_boundary,
                'Content-Disposition: file; name="{}"; filename="{}"'.format(
                    field_name, filename
                ),
                'Content-Type: {}'.format(content_type),
                '',
                body,
            ])

        parts.append('--' + self.boundary + '--')
        parts.append('')

        # "RFC-1521 dictates that MIME streams have lines terminated by CRLF ("\r\n")." Source:
        # http://search.cpan.org/~eryq/MIME-tools-6.200_02/lib/MIME/Tools/traps.pod#Fuzzing_of_CRLF_and_newline_on_input
        return '\r\n'.join(parts)


def login(email, password, server_url):
    """Authenticate the user."""

    api_key = None
    username = None

    try:
        login_result = urllib2.urlopen(
            '{}/footprint/login/'.format(server_url),
            data=urllib.urlencode({'email': email, 'password': password, 'output': 'json'}),
            **ssl_context_kwarg
        )
    except urllib2.HTTPError, e:
        if e.code != 200:
            raise arcpy.ExecuteError("Incorrect Email/Password combination. Please try again.")
    # raise error to user if url request fails
    except urllib2.URLError, e:
        raise arcpy.ExecuteError("Error reaching {}. Please check the Server URL and try again.".format(server_url))
    # raise error if url is not valid
    except ValueError, e:
        raise arcpy.ExecuteError("{} is not a valid url. Please check the Server URL and try again.".format(server_url))

    try:
        user_data = json.loads(login_result.read())
    except ValueError:
        raise arcpy.ExecuteError("Login attempt returned invalid response.")

    if user_data and 'objects' in user_data:
        if len(user_data['objects']):
            api_key = user_data['objects'][0]['api_key']
            username = user_data['objects'][0]['username']

    return username, api_key


def get_config_entity_id(username, api_key, config_entity_name, server_url):
    """Make an API query of Projects by name and return the id."""

    config_entity_id = None

    url = '{}/footprint/api/v1/project/?format=json&username={}&api_key={}&name={}'.format(
            server_url, urllib.quote(username), urllib.quote(api_key), urllib.quote(config_entity_name))

    config_entity_result = urllib2.urlopen(
        url,
        **ssl_context_kwarg
    )

    try:
        config_entity_data = json.loads(config_entity_result.read())
    except ValueError:
        raise arcpy.ExecuteError("Project lookup returned invalid response.")

    if config_entity_data and 'objects' in config_entity_data:
        if len(config_entity_data['objects']):
            config_entity_id = config_entity_data['objects'][0]['id']

    return config_entity_id



def get_input_filepath(layer):
    """Try to get the full filepath using arcpy.Describe
    except IOError for gdbs with full filepaths in which
    case we already have the filepath"""

    try:
        desc = arcpy.Describe(layer)
        layersource = desc.catalogPath

    except IOError:
        layersource = layer

    return layersource

def get_file_extension(layer):
    """Try to get the file extension using arcpy.Describe
    except throws an IOError for gdbs with full filepaths"""

    try:
        file_extension = arcpy.Describe(layer).extension
    except IOError:
        file_extension = ''

    return file_extension
