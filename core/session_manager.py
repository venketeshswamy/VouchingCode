# ocr_tool_qt/core/session_manager.py

import json
import os
import shutil
import zipfile
from datetime import datetime
from utils.logger import log

class SessionManager:
    """
    Handles saving and loading of the application state, including files,
    templates, and results.
    """
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.imports_dir = os.path.join(self.config_manager.get('workspace_dir'), 'imports')
        self.exports_dir = os.path.join(self.config_manager.get('workspace_dir'), 'exports')

    def save_session(self, filepath, image_paths, templates, ocr_results, ui_settings):
        """
        Saves the current session state to a .ocrtool_session zip file.
        
        Args:
            filepath (str): The path to save the session file.
            image_paths (list): List of full paths to the imported files.
            templates (list): List of template dictionaries.
            ocr_results (list): List of OCR result dictionaries.
            ui_settings (dict): Dictionary of current UI settings to save.
        """
        log.info(f"Saving session to {filepath}...")
        
        templates_to_save = []
        for t_orig in templates:
            t_copy = t_orig.copy()
            # NumPy array is not JSON serializable and should be derived on load
            t_copy.pop('image_np_array', None) 
            templates_to_save.append(t_copy)

        session_data = {
            'version': '3.0-qt',
            'image_basenames': [os.path.basename(p) for p in image_paths],
            'templates': templates_to_save,
            'ocr_results': ocr_results,
            'ui_settings': ui_settings
        }

        try:
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Write metadata
                zf.writestr('session_data.json', json.dumps(session_data, indent=4))
                
                # Write imported documents
                docs_subdir_in_zip = "imported_documents"
                for local_import_path in image_paths:
                    if os.path.exists(local_import_path):
                        zf.write(local_import_path, os.path.join(docs_subdir_in_zip, os.path.basename(local_import_path)))
                    else:
                        log.warning(f"File not found during session save: {local_import_path}")
            log.info("Session saved successfully.")
            return True
        except Exception as e:
            log.error(f"Failed to save session to {filepath}: {e}", exc_info=True)
            return False

    def load_session(self, filepath):
        """
        Loads a session from a .ocrtool_session file.

        Args:
            filepath (str): The path to the session file to load.

        Returns:
            A dictionary containing the loaded session data, or None on failure.
        """
        log.info(f"Loading session from {filepath}...")
        self.clear_current_imports()

        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                if 'session_data.json' not in zf.namelist():
                    log.error("Invalid session file: 'session_data.json' not found.")
                    return None

                session_data = json.loads(zf.read('session_data.json'))
                
                # Extract documents
                docs_subdir_in_zip = "imported_documents"
                extracted_paths = []
                for member_info in zf.infolist():
                    if member_info.filename.startswith(docs_subdir_in_zip + "/") and not member_info.is_dir():
                        target_path = os.path.join(self.imports_dir, os.path.basename(member_info.filename))
                        with zf.open(member_info) as source, open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                        extracted_paths.append(target_path)

                # The main window will use this data to populate the app state
                session_data['image_paths'] = extracted_paths
                log.info("Session loaded successfully.")
                return session_data

        except zipfile.BadZipFile:
            log.error(f"Invalid or corrupted session file: {filepath}")
            return None
        except Exception as e:
            log.error(f"Failed to load session from {filepath}: {e}", exc_info=True)
            return None
            
    def copy_file_to_imports(self, original_path):
        """Copies a single file to the imports directory and returns the new path."""
        if not os.path.exists(original_path):
            log.error(f"Cannot import file, path does not exist: {original_path}")
            return None
        
        base_name = os.path.basename(original_path)
        local_copy_path = os.path.join(self.imports_dir, base_name)
        
        try:
            shutil.copy2(original_path, local_copy_path)
            log.info(f"Copied '{base_name}' to imports directory.")
            return local_copy_path
        except Exception as e:
            log.error(f"Could not copy '{base_name}' to imports directory: {e}")
            return None

    def clear_current_imports(self):
        """Removes all files from the imports directory."""
        if not os.path.exists(self.imports_dir):
            return
        for filename in os.listdir(self.imports_dir):
            file_path = os.path.join(self.imports_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                log.error(f'Failed to delete {file_path}. Reason: {e}')
