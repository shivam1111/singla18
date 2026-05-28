from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import logging,os
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)
# External library imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    logging.getLogger(__name__).warning("Please run: pip3 install google-api-python-client google-auth")

class MillGoogleDriveWizard(models.TransientModel):
    _name = 'mill.google.drive.wizard'
    _description = 'Mill Google Drive Finder'

    file_query = fields.Char(string="Enter Item Code / File Name", required=True)
    mds_iframe_url = fields.Html(string="Document Preview",sanitize=False, strip_style=False)

    def action_open_mill_mds_viewer(self):
        self.ensure_one()
        # This opens the wizard we created earlier
        return {
            'name': _('MDS Finder'),
            'type': 'ir.actions.act_window',
            'res_model': 'mill.google.drive.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                # Pre-fill the search box with the Item Code (Internal Reference)
                # 'default_file_query': self.product_id.default_code,
            }
        }

    def _get_drive_service(self):
        """ Dynamically finds the JSON file inside the module folder """
        try:
            # This replaces get_resource_path and get_module_resource
            # Format: 'module_name/path/to/file'
            json_path = tools.file_path('mill_core/data/credentials.json')
        except FileNotFoundError:
            raise UserError(_("JSON Credentials file not found in the module data folder."))
        # If it's in the root of the module, use:
        # json_path = get_module_resource('mill_google_drive', 'credentials.json')

        if not json_path or not os.path.exists(json_path):
            raise UserError(_("JSON Credentials file not found at %s") % json_path)

        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        creds = service_account.Credentials.from_service_account_file(json_path, scopes=SCOPES)
        return build('drive', 'v3', credentials=creds,cache_discovery=False)

    def action_search_file(self):
        self.ensure_one()
        service = self._get_drive_service()
        # Use 'contains' for flexibility or '=' for strict matching
        # and use 'name' comparison that is case-insensitive where possible
        search_term = self.file_query.strip()
        query = f"name contains '{search_term}' and mimeType = 'application/pdf' and trashed = false"
        try:
            # We ask for 'webViewLink' as well just in case you want a direct link later
            results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
            files = results.get('files', [])
            if files:
                file_id = files[0]['id']
                # IMPORTANT: Use the /preview link for embedding
                preview_url = f"https://drive.google.com/file/d/{file_id}/preview"

                # We wrap the iframe in a div for better display
                self.mds_iframe_url = f"""
                        <div style="width:100%; height:750px; border: 1px solid #ccc;">
                            <iframe src="{preview_url}" 
                                    width="100%" 
                                    height="100%" 
                                    frameborder="0" 
                                    allow="autoplay">
                            </iframe>
                        </div>
                    """
            else:
                self.mds_iframe_url = "<p>No file found.</p>"
        except Exception as e:
            self.mds_iframe_url = f"<div class='alert alert-danger'>Google API Error: {str(e)}</div>"

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }