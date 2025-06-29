import os
import json
import csv
from tkinter import filedialog, messagebox

class ProfileManager:
    """Manages custom airfoil profiles loading and validation"""
    
    def __init__(self, naca_data_dict, profile_info_dict):
        """
        Initialize ProfileManager
        
        Args:
            naca_data_dict: Reference to the main naca_data dictionary
            profile_info_dict: Reference to the profile_info dictionary
        """
        self.naca_data = naca_data_dict
        self.profile_info = profile_info_dict
        self.custom_profiles_file = "calculations/custom_profiles.json"
        self.load_custom_profiles()
    
    def load_custom_profiles(self):
        """Load previously saved custom profiles"""
        if os.path.exists(self.custom_profiles_file):
            try:
                with open(self.custom_profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Add custom profiles to main data
                    for profile_name, profile_data in data.get('profiles', {}).items():
                        if profile_name not in self.naca_data:
                            self.naca_data[profile_name] = profile_data
                    # Add custom profile info
                    for profile_name, info in data.get('profile_info', {}).items():
                        if profile_name not in self.profile_info:
                            self.profile_info[profile_name] = info
            except Exception as e:
                print(f"Error loading custom profiles: {e}")
    
    def save_custom_profiles(self):
        """Save custom profiles to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.custom_profiles_file), exist_ok=True)
            
            # Find custom profiles (not standard NACA)
            standard_profiles = ["NACA 2412", "NACA 0012", "NACA 4412", "NACA 2415", 
                                "NACA 6409", "NACA 0015", "NACA 23012", "NACA 64A010"]
            
            custom_profiles = {}
            custom_info = {}
            
            for profile_name, profile_data in self.naca_data.items():
                if profile_name not in standard_profiles:
                    custom_profiles[profile_name] = profile_data
                    
            for profile_name, info in self.profile_info.items():
                if profile_name not in standard_profiles:
                    custom_info[profile_name] = info
            
            # Save to file
            data_to_save = {
                'profiles': custom_profiles,
                'profile_info': custom_info
            }
            
            with open(self.custom_profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving custom profiles: {e}")
    
    def validate_profile_data(self, alpha_values, cl_values, cd_values):
        """
        Validate profile data format and values
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if all lists have same length
        if not (len(alpha_values) == len(cl_values) == len(cd_values)):
            return False, "All data columns must have the same length"
        
        # Check minimum number of points
        if len(alpha_values) < 3:
            return False, "Profile must have at least 3 data points"
        
        # Check if alpha values are numeric and in reasonable range (range is larger than the app can calculate for)
        try:
            alpha_numeric = [float(x) for x in alpha_values]
            if min(alpha_numeric) < -30 or max(alpha_numeric) > 30:
                return False, "Angle of attack values should be between -30° and 30°"
        except (ValueError, TypeError):
            return False, "Angle of attack values must be numeric"
        
        # Check if CL values are numeric and in reasonable range
        try:
            cl_numeric = [float(x) for x in cl_values]
            if min(cl_numeric) < -3 or max(cl_numeric) > 3:
                return False, "CL values should be between -3 and 3"
        except (ValueError, TypeError):
            return False, "CL values must be numeric"
        
        # Check if CD values are numeric and positive
        try:
            cd_numeric = [float(x) for x in cd_values]
            if min(cd_numeric) < 0 or max(cd_numeric) > 1:
                return False, "CD values should be between 0 and 1"
        except (ValueError, TypeError):
            return False, "CD values must be numeric"
        
        # Check if alpha values are sorted
        if alpha_numeric != sorted(alpha_numeric):
            return False, "Angle of attack values should be in ascending order"
        
        return True, "Valid profile data"
    
    def load_profile_from_file(self):
        """
        Load profile from file (CSV or TXT)
        Expected formats:
        CSV: alpha,CL,CD (with headers)
        TXT: space or tab separated: alpha CL CD
        
        Returns:
            tuple: (success, profile_name or error_message)
        """
        filetypes = [
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Profile Data File",
            filetypes=filetypes
        )
        
        if not filepath:
            return False, "No file selected"
        
        try:
            # Try to determine file format and load
            if filepath.lower().endswith('.csv'):
                return self._load_csv_file(filepath)
            else:
                return self._load_txt_file(filepath)
                
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def _load_csv_file(self, filepath):
        """Load CSV file with headers: alpha,CL,CD"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                alpha_values = []
                cl_values = []
                cd_values = []
                
                # Try different possible column names
                alpha_cols = ['alpha', 'Alpha', 'ALPHA', 'angle', 'Angle', 'AOA', 'aoa']
                cl_cols = ['CL', 'cl', 'Cl', 'lift', 'Lift', 'CL_coeff']
                cd_cols = ['CD', 'cd', 'Cd', 'drag', 'Drag', 'CD_coeff']
                
                # Find correct column names
                headers = reader.fieldnames
                alpha_col = next((col for col in alpha_cols if col in headers), None)
                cl_col = next((col for col in cl_cols if col in headers), None)
                cd_col = next((col for col in cd_cols if col in headers), None)
                
                if not all([alpha_col, cl_col, cd_col]):
                    return False, f"Required columns not found. Expected columns like: alpha, CL, CD. Found: {headers}"
                
                for row in reader:
                    try:
                        alpha_values.append(float(row[alpha_col]))
                        cl_values.append(float(row[cl_col]))
                        cd_values.append(float(row[cd_col]))
                    except ValueError:
                        continue  # Skip invalid rows
                
                return self._process_loaded_data(filepath, alpha_values, cl_values, cd_values)
                
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}"
    
    def _load_txt_file(self, filepath):
        """Load TXT file with format: alpha CL CD (space/tab separated)"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            alpha_values = []
            cl_values = []
            cd_values = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                    
                # Split by whitespace
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        alpha_values.append(float(parts[0]))
                        cl_values.append(float(parts[1]))
                        cd_values.append(float(parts[2]))
                    except ValueError:
                        continue  # Skip invalid lines
            
            return self._process_loaded_data(filepath, alpha_values, cl_values, cd_values)
            
        except Exception as e:
            return False, f"Error reading TXT file: {str(e)}"
    
    def _process_loaded_data(self, filepath, alpha_values, cl_values, cd_values):
        """Process and validate loaded data"""
        if not alpha_values:
            return False, "No valid data found in file"
        
        # Validate data
        is_valid, message = self.validate_profile_data(alpha_values, cl_values, cd_values)
        if not is_valid:
            return False, f"Data validation failed: {message}"
        
        # Generate profile name from filename
        filename = os.path.basename(filepath)
        profile_name = os.path.splitext(filename)[0].upper()
        
        # Make sure name is unique
        original_name = profile_name
        counter = 1
        while profile_name in self.naca_data:
            profile_name = f"{original_name}_{counter}"
            counter += 1
        
        # Add profile to data
        self.naca_data[profile_name] = {
            "alpha": alpha_values,
            "CL": cl_values,
            "CD": cd_values
        }
        
        # Add basic info
        self.profile_info[profile_name] = f"Custom profile loaded from {filename}"
        
        # Save custom profiles
        self.save_custom_profiles()
        
        return True, profile_name
    
    def remove_custom_profile(self, profile_name):
        """Remove a custom profile"""
        standard_profiles = ["NACA 2412", "NACA 0012", "NACA 4412", "NACA 2415", 
                            "NACA 6409", "NACA 0015", "NACA 23012", "NACA 64A010"]
        
        if profile_name in standard_profiles:
            return False, "Cannot remove standard NACA profiles"
        
        if profile_name in self.naca_data:
            del self.naca_data[profile_name]
            
        if profile_name in self.profile_info:
            del self.profile_info[profile_name]
            
        self.save_custom_profiles()
        return True, f"Profile {profile_name} removed successfully"