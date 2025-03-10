# main.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, StringVar, filedialog
import threading
from pylablib.devices import Thorlabs
from camera import Camera
from cameragui import CameraGUI
from stage import Stage
from xStage import XiStage, default_params
import libximc.highlevel as ximc  # Import for Standa stage enumeration
from stagegui import StageGUI
from scan import Scan, Scanner_Backend

class ImagingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XY Imaging Application")
        self.root.geometry("800x600")
        
        # Initialize backend with no hardware by default (simulation mode)
        self.backend = Scanner_Backend()
        
        # Lists to store available devices
        self.ximc_devices = []
        
        # Set up tabs and main UI structure
        self.create_widgets()
        
        # Make sure we close everything properly when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.stage_tab = ttk.Frame(self.notebook)
        self.camera_tab = ttk.Frame(self.notebook)
        self.scan_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.stage_tab, text="Stage Control")
        self.notebook.add(self.camera_tab, text="Camera Control")
        self.notebook.add(self.scan_tab, text="Scan Setup")
        self.notebook.add(self.config_tab, text="Hardware Config")
        
        # Setup hardware config tab first
        self.setup_config_tab(self.config_tab)
        
        # Initialize other tabs
        self.setup_stage_tab(self.stage_tab)
        self.setup_camera_tab(self.camera_tab)
        self.setup_scan_tab(self.scan_tab)
        
    def setup_config_tab(self, parent):
        """Setup tab for hardware configuration"""
        config_frame = ttk.LabelFrame(parent, text="Hardware Configuration")
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        enumeratrion_buttons_frame = tk.Frame(config_frame)
        enumeratrion_buttons_frame.pack(fill="x", padx=10, pady=5)

        # Button to enumerate XIMC devices
        enumerateX_frame = ttk.Frame(enumeratrion_buttons_frame)
        enumerateX_frame.pack(side='right', padx=5, pady=5)
        ttk.Button(enumerateX_frame, text="Enumerate Standa Stages", 
                  command=self.enumerate_ximc_devices).pack(pady=10)
        
        # Button to enumerate THOR devices
        enumerateT_frame = ttk.Frame(enumeratrion_buttons_frame)
        enumerateT_frame.pack(side='right', padx=5, pady=5)
        ttk.Button(enumerateT_frame, text="Enumerate Thor Stages", 
                  command=self.enumerate_thor_devices).pack(pady=10)

        # Button to enumerate cameras devices
        enumerateC_frame = ttk.Frame(enumeratrion_buttons_frame)
        enumerateC_frame.pack(side='right', padx=5, pady=5)
        ttk.Button(enumerateC_frame, text="Enumerate Cameras", 
                  command=self.enumerate_cameras).pack(pady=10)

        # X Stage Configuration
        x_stage_frame = ttk.Frame(config_frame)
        x_stage_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(x_stage_frame, text="X Stage Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.x_stage_type = StringVar(value="Thorlabs")
        x_type_combo = ttk.Combobox(x_stage_frame, textvariable=self.x_stage_type, 
                                   values=["Thorlabs", "Standa"], state="readonly", width=10)
        x_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(x_stage_frame, text="X Stage SN/URI:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.x_stage_sn = ttk.Combobox(x_stage_frame, width=30)
        self.x_stage_sn.grid(row=0, column=3, padx=5, pady=5)
        
        self.x_stage_status = ttk.Label(x_stage_frame, text="Not Connected")
        self.x_stage_status.grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(x_stage_frame, text="Connect", 
                  command=lambda: self.connect_stage('x')).grid(row=0, column=5, padx=5, pady=5)
        
        # Y Stage Configuration
        y_stage_frame = ttk.Frame(config_frame)
        y_stage_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(y_stage_frame, text="Y Stage Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.y_stage_type = StringVar(value="Thorlabs")
        y_type_combo = ttk.Combobox(y_stage_frame, textvariable=self.y_stage_type, 
                                   values=["Thorlabs", "Standa"], state="readonly", width=10)
        y_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(y_stage_frame, text="Y Stage SN/URI:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.y_stage_sn = ttk.Combobox(y_stage_frame, width=30)
        self.y_stage_sn.grid(row=0, column=3, padx=5, pady=5)
        
        self.y_stage_status = ttk.Label(y_stage_frame, text="Not Connected")
        self.y_stage_status.grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(y_stage_frame, text="Connect", 
                  command=lambda: self.connect_stage('y')).grid(row=0, column=5, padx=5, pady=5)
        
        # Camera Configuration
        camera_frame = ttk.Frame(config_frame)
        camera_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(camera_frame, text="Camera SN:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.camera_sn = ttk.Entry(camera_frame, width=20)
        self.camera_sn.grid(row=0, column=1, padx=5, pady=5)
        self.camera_status = ttk.Label(camera_frame, text="Not Connected")
        self.camera_status.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(camera_frame, text="Connect", 
                  command=self.connect_camera).grid(row=0, column=3, padx=5, pady=5)
        
        # Refresh all hardware connections
        refresh_frame = ttk.Frame(config_frame)
        refresh_frame.pack(fill="x", padx=10, pady=20)
        
        ttk.Button(refresh_frame, text="Reset/Disconnect All", 
                  command=self.reset_hardware).pack(pady=10)
                  
        # Initialize with simulation mode button
        ttk.Button(refresh_frame, text="Use Simulation Mode", 
                  command=self.use_simulation).pack(pady=10)
                  
        # Set up callback when stage type changes
        x_type_combo.bind("<<ComboboxSelected>>", lambda e: self.on_stage_type_change('x'))
        y_type_combo.bind("<<ComboboxSelected>>", lambda e: self.on_stage_type_change('y'))
    
    def enumerate_thor_devices(self):
        """Enumerate available kenisis devices"""
        try:
            # Enumerate devices with the ENUMERATE_PROBE flag to get full information
            self.thor_devices =  Thorlabs.list_kinesis_devices()
            
            if not self.thor_devices:
                messagebox.showinfo("Device Enumeration", "No Thorlabs Kenisis devices found.")
                return
                
            # Create list of device URIs for the comboboxes
            device_list = []
            device_info = []
            
            for device in self.thor_devices:
                sn = device[0] # [('27500001', 'Kinesis K-Cube  DC Driver')]
                device_list.append(sn)
                # Format information about the device
                info = f"{device[1]} - SN:{device[sn]}"
                device_info.append(info)
                
            # Update both comboboxes
            self.x_stage_sn['values'] = device_list
            self.y_stage_sn['values'] = device_list
            
            # Show enumerated devices
            devices_str = "\n".join(device_info)
            messagebox.showinfo("Found Devices", f"Found {len(self.thor_devices)} Kenisis devices:\n\n{devices_str}")
            
        except Exception as e:
            messagebox.showerror("Enumeration Error", f"Failed to enumerate THOR devices: {e}")
     
    def enumerate_ximc_devices(self):
        """Enumerate available Standa XIMC devices"""
        try:
            # Enumerate devices with the ENUMERATE_PROBE flag to get full information
            self.ximc_devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_PROBE)
            
            if not self.ximc_devices:
                messagebox.showinfo("Device Enumeration", "No Standa XIMC devices found.")
                return
                
            # Create list of device URIs for the comboboxes
            device_list = []
            device_info = []
            
            for device in self.ximc_devices:
                uri = device['uri']
                device_list.append(uri)
                # Format information about the device
                info = f"{device['PositionerName']} - SN:{device['device_serial']}"
                device_info.append(info)
                
            # Update both comboboxes
            self.x_stage_sn['values'] = device_list
            self.y_stage_sn['values'] = device_list
            
            # Show enumerated devices
            devices_str = "\n".join(device_info)
            messagebox.showinfo("Found Devices", f"Found {len(self.ximc_devices)} Standa devices:\n\n{devices_str}")
            
        except Exception as e:
            messagebox.showerror("Enumeration Error", f"Failed to enumerate XIMC devices: {e}")

    def enumerate_cameras(self):
        """Enumerate available thorlabs cameras"""
        try:
            # Enumerate devices with the ENUMERATE_PROBE flag to get full information
            self.cam_devices =  Thorlabs.list_cameras_tlcam()
            
            if not self.cam_devices:
                messagebox.showinfo("Device Enumeration", "No Thorlabs Camera found.")
                return
                
            # Create list of device URIs for the comboboxes
            device_list = []
            device_info = []
            
            for device in self.cam_devices:
                sn = device # ['12001', '12002']
                device_list.append(sn)
                # Format information about the device
                info = f"Thorlabs camera SN:{sn}"
                device_info.append(info)
                
            # Update combobox
            self.camera_sn['values'] = device_list
            
            # Show enumerated devices
            devices_str = "\n".join(device_info)
            messagebox.showinfo("Found Devices", f"Found {len(self.cam_devices)} Kenisis devices:\n\n{devices_str}")
            
        except Exception as e:
            messagebox.showerror("Enumeration Error", f"Failed to enumerate XIMC devices: {e}")
    



    def on_stage_type_change(self, axis):
        """Handle stage type selection change"""
        stage_type = self.x_stage_type.get() if axis == 'x' else self.y_stage_type.get()
        stage_combo = self.x_stage_sn if axis == 'x' else self.y_stage_sn
        
        if stage_type == "Standa":
            # If we have enumerated XIMC devices, populate the combobox
            if self.ximc_devices:
                uris = [device['uri'] for device in self.ximc_devices]
                stage_combo['values'] = uris
            else:
                # If no enumeration has been done, prompt user
                messagebox.showinfo("Device Selection", 
                                   "Please use 'Enumerate Standa Stages' to find available devices")
                stage_combo['values'] = []
        else:
            # If we have enumerated THOR devices, populate the combobox
            if self.thor_devices:
                sns = [device['sn'] for device in self.thor_devices]
                stage_combo['values'] = sns
            else:
                # If no enumeration has been done, prompt user
                messagebox.showinfo("Device Selection", 
                                   "Please use 'Enumerate Thor Stages' to find available devices")
                stage_combo['values'] = []
    
    def setup_stage_tab(self, parent):
        """Setup tab for stage control"""
        # We'll replace this with actual StageGUI instances when stages are connected
        self.x_stage_gui_frame = ttk.LabelFrame(parent, text="X Stage")
        self.x_stage_gui_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(self.x_stage_gui_frame, 
                 text="X Stage not connected. Configure in Hardware Config tab.").pack(padx=20, pady=20)
        
        self.y_stage_gui_frame = ttk.LabelFrame(parent, text="Y Stage")
        self.y_stage_gui_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(self.y_stage_gui_frame, 
                 text="Y Stage not connected. Configure in Hardware Config tab.").pack(padx=20, pady=20)
    
    def setup_camera_tab(self, parent):
        """Setup tab for camera control"""
        # We'll replace this with actual CameraGUI instance when camera is connected
        self.camera_gui_frame = ttk.LabelFrame(parent, text="Camera Control")
        self.camera_gui_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ttk.Label(self.camera_gui_frame, 
                 text="Camera not connected. Configure in Hardware Config tab.").pack(padx=20, pady=20)
        
        # Initialize camera GUI with whatever camera is available (could be simulation)
        self.refresh_camera_gui()
    
    def setup_scan_tab(self, parent):
        """Setup tab for scan control"""
        # Scan parameters frame
        param_frame = ttk.LabelFrame(parent, text="Scan Parameters")
        param_frame.pack(fill="x", padx=10, pady=5)
        
        # Number of steps
        ttk.Label(param_frame, text="Number of X steps:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_x_entry = ttk.Entry(param_frame, width=10)
        self.num_x_entry.insert(0, "5")
        self.num_x_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Number of Y steps:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.num_y_entry = ttk.Entry(param_frame, width=10)
        self.num_y_entry.insert(0, "5")
        self.num_y_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Resolution
        ttk.Label(param_frame, text="X Resolution:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.res_x_entry = ttk.Entry(param_frame, width=10)
        self.res_x_entry.insert(0, "1.0")
        self.res_x_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Y Resolution:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.res_y_entry = ttk.Entry(param_frame, width=10)
        self.res_y_entry.insert(0, "1.0")
        self.res_y_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Pattern selection
        self.pattern_var = tk.BooleanVar(value=True)
        pattern_frame = ttk.Frame(param_frame)
        pattern_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        ttk.Radiobutton(pattern_frame, text="Snake Pattern", variable=self.pattern_var, 
                       value=True).pack(side="left", padx=5)
        ttk.Radiobutton(pattern_frame, text="Ladder Pattern", variable=self.pattern_var, 
                       value=False).pack(side="left", padx=5)
        
        # Apply button
        ttk.Button(param_frame, text="Apply Settings", command=self.apply_scan_settings).grid(
            row=5, column=0, columnspan=2, padx=5, pady=10)
        
        # output frame
        save_frame = ttk.LabelFrame(parent, text="Image Saving Config")
        save_frame.pack(fill="x", padx=10, pady=5)

        # Output folder selection
        folder_frame = ttk.Frame(save_frame)
        folder_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(folder_frame, text="Output Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=40)
        folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        def browse_folder():
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                self.folder_var.set(folder_selected)

        browse_button = ttk.Button(folder_frame, text="Browse", command=browse_folder)
        browse_button.grid(row=0, column=2, padx=5, pady=5)

        # Configure column weights for proper expansion
        folder_frame.columnconfigure(1, weight=1)

        # Image prefix entry
        prefix_frame = ttk.Frame(save_frame)
        prefix_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(prefix_frame, text="Image Prefix:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.prefix_var = tk.StringVar(value="image_")
        prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=40)
        prefix_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Configure column weights for proper expansion
        prefix_frame.columnconfigure(1, weight=1)

        # Save options
        options_frame = ttk.Frame(save_frame)
        options_frame.pack(fill="x", padx=10, pady=5)

        self.auto_save_var = tk.BooleanVar(value=True)
        auto_save_check = ttk.Checkbutton(
            options_frame, 
            text="Auto-save images", 
            variable=self.auto_save_var
        )
        auto_save_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.overwrite_var = tk.BooleanVar(value=False)
        overwrite_check = ttk.Checkbutton(
            options_frame, 
            text="Overwrite existing files", 
            variable=self.overwrite_var
        )
        overwrite_check.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Apply settings button for saving configuration
        apply_save_button = ttk.Button(
            save_frame, 
            text="Apply Save Settings", 
            command=self.apply_save_settings
        )
        apply_save_button.pack(padx=10, pady=10)


        # Configure column weights for proper expansion
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        # Control frame
        control_frame = ttk.LabelFrame(parent, text="Scan Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start Scan", command=self.start_scan)
        self.start_button.grid(row=0, column=0, padx=5, pady=10)
        
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_scan, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=5, pady=10)
        
        self.resume_button = ttk.Button(control_frame, text="Resume", command=self.resume_scan, state="disabled")
        self.resume_button.grid(row=0, column=2, padx=5, pady=10)
        
        self.cancel_button = ttk.Button(control_frame, text="Cancel", command=self.cancel_scan, state="disabled")
        self.cancel_button.grid(row=0, column=3, padx=5, pady=10)
        
        # Status frame
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.scan_status = ttk.Label(status_frame, text="Ready")
        self.scan_status.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(status_frame, text="Progress:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
        self.progress_bar.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        

        # Check if scan is possible
        self.update_scan_ui_state()
    

    def apply_save_settings(self):
        """Apply the image saving settings to the scanner"""
        folder = self.folder_var.get()
        prefix = self.prefix_var.get()
        auto_save = self.auto_save_var.get()
        overwrite = self.overwrite_var.get()
        
        # Validate folder path
        if not folder:
            messagebox.showerror("Error", "Please select an output folder")
            return
        
        # Validate prefix
        if not prefix:
            messagebox.showerror("Error", "Please enter an image prefix")
            return
        
        # Apply settings to scanner backend
        success = self.backend.setup_scan_saving(folder, prefix, auto_save, overwrite)
        
        if success:
            messagebox.showinfo("Success", "Image saving settings applied")
        else:
            messagebox.showerror("Error", "Failed to apply save settings")

    def connect_stage(self, axis):
        """Connect to a stage with the given serial number or URI"""
        stage_type = self.x_stage_type.get() if axis == 'x' else self.y_stage_type.get()
        sn_or_uri = self.x_stage_sn.get() if axis == 'x' else self.y_stage_sn.get()
        
        if not sn_or_uri and stage_type != "Standa":
            # Use simulation mode if no SN provided
            sn_or_uri = None
            
        try:
            # Create appropriate stage based on type
            if stage_type == "Thorlabs":
                # Use original Stage class for Thorlabs devices
                if axis == 'x':
                    self.backend.x_stage = Stage("X", sn_or_uri)
                else:
                    self.backend.y_stage = Stage("Y", sn_or_uri)
                    
                # Update status label
                status_text = "Connected" if sn_or_uri else "Simulation Mode"
                
            elif stage_type == "Standa":
                # Use XiStage for Standa devices
                if not sn_or_uri:
                    messagebox.showerror("Connection Error", "Please select a Standa device URI")
                    return
                    
                stage_name = f"{axis.upper()} Standa Stage"
                
                # Create a custom name for the stage
                if axis == 'x':
                    new_xi_params = default_params
                    new_xi_params.address = sn_or_uri
                    self.backend.x_stage = XiStage(xi_params=new_xi_params,name=stage_name)
                    # Override the default address with the selected one
                    self.backend.x_stage._connect_stage()
                else:
                    new_xi_params = default_params
                    new_xi_params.address = sn_or_uri
                    self.backend.y_stage = XiStage(xi_params=new_xi_params,name=stage_name)
                    # Override the default address with the selected one
                    self.backend.y_stage.axis.params.address = sn_or_uri
                    self.backend.y_stage._connect_stage()
                
                status_text = "Connected (Standa)"
            
            # Update status label
            if axis == 'x':
                self.x_stage_status.config(text=status_text)
                # Update the stage GUI
                self.refresh_x_stage_gui()
            else:
                self.y_stage_status.config(text=status_text)
                # Update the stage GUI
                self.refresh_y_stage_gui()
                
            # Update scan object with new stage
            self.refresh_scan_object()
            
            # Update UI state for scan tab
            self.update_scan_ui_state()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {axis.upper()} stage: {e}")
    
    def connect_camera(self):
        """Connect to camera with the given serial number"""
        sn = self.camera_sn.get()
        
        if not sn:
            # Use simulation mode if no SN provided
            sn = None
            
        try:
            # Close existing camera first
            if self.backend.camera:
                self.backend.camera.close()
                
            # Create new camera
            self.backend.camera = Camera(sn)
            self.camera_status.config(text="Connected" if sn else "Simulation Mode")
            
            # Refresh the camera GUI
            self.refresh_camera_gui()
            
            # Update scan object with new camera
            self.refresh_scan_object()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to camera: {e}")
    
    def refresh_x_stage_gui(self):
        """Refresh the X stage GUI with the current stage object"""
        # Clear the existing content
        for widget in self.x_stage_gui_frame.winfo_children():
            widget.destroy()
            
        if self.backend.x_stage:
            # Create new StageGUI instance
            StageGUI(self.x_stage_gui_frame, self.backend.x_stage)
        else:
            # No stage connected
            ttk.Label(self.x_stage_gui_frame, 
                     text="X Stage not connected. Configure in Hardware Config tab.").pack(padx=20, pady=20)
    
    def refresh_y_stage_gui(self):
        """Refresh the Y stage GUI with the current stage object"""
        # Clear the existing content
        for widget in self.y_stage_gui_frame.winfo_children():
            widget.destroy()
            
        if self.backend.y_stage:
            # Create new StageGUI instance
            StageGUI(self.y_stage_gui_frame, self.backend.y_stage)
        else:
            # No stage connected
            ttk.Label(self.y_stage_gui_frame, 
                     text="Y Stage not connected. Configure in Hardware Config tab.").pack(padx=20, pady=20)
    
    def refresh_camera_gui(self):
        """Refresh the camera GUI with the current camera object"""
        # Clear the existing content
        for widget in self.camera_gui_frame.winfo_children():
            widget.destroy()
            
        if self.backend.camera:
            # Create new CameraGUI instance
            CameraGUI(self.camera_gui_frame, self.backend.camera)

        else:
            # No camera connected
            ttk.Label(self.camera_gui_frame, 
                     text="Camera not connected. Configure in Hardware Config tab.").pack(padx=20, pady=20)
    
    def refresh_scan_object(self):
        """Recreate the scan object with current hardware"""
        # Recreate scan with current hardware
        self.backend.scan = Scan(self.backend.camera, self.backend.x_stage, self.backend.y_stage)
    
    def reset_hardware(self):
        """Reset all hardware connections"""
        # Confirm with user
        if messagebox.askyesno("Confirm Reset", "This will disconnect all hardware. Continue?"):
            # Close existing hardware
            self.backend.close()
            
            # Create new backend
            self.backend = Scanner_Backend()
            
            # Update UI
            self.x_stage_status.config(text="Not Connected")
            self.y_stage_status.config(text="Not Connected")
            self.camera_status.config(text="Not Connected")
            
            # Refresh GUIs
            self.refresh_x_stage_gui()
            self.refresh_y_stage_gui()
            self.refresh_camera_gui()
            
            # Update scan UI state
            self.update_scan_ui_state()
    
    def use_simulation(self):
        """Switch to simulation mode for all hardware"""
        # Confirm with user
        if messagebox.askyesno("Confirm Simulation", "This will set all hardware to simulation mode. Continue?"):
            # Close existing hardware
            self.backend.close()
            
            # Create new backend with simulation mode
            self.backend = Scanner_Backend()
            
            # Create simulation devices
            self.backend.x_stage = Stage("X")  # No SN = simulation
            self.backend.y_stage = Stage("Y")  # No SN = simulation
            self.backend.camera = Camera()  # No SN = simulation
            
            # Refresh scan object
            self.refresh_scan_object()
            
            # Update UI
            self.x_stage_status.config(text="Simulation Mode")
            self.y_stage_status.config(text="Simulation Mode")
            self.camera_status.config(text="Simulation Mode")
            
            # Refresh GUIs
            self.refresh_x_stage_gui()
            self.refresh_y_stage_gui()
            self.refresh_camera_gui()
            
            # Update scan UI state
            self.update_scan_ui_state()
    
    def apply_scan_settings(self):
        """Apply scan settings to the scan object"""
        try:
            num_x = int(self.num_x_entry.get())
            num_y = int(self.num_y_entry.get())
            res_x = float(self.res_x_entry.get())
            res_y = float(self.res_y_entry.get())
            pattern = self.pattern_var.get()
            
            if self.backend.scan:
                self.backend.scan.setup_scan(num_x, num_y, res_x, res_y, pattern)
                self.scan_status.config(text="Settings applied")
            else:
                self.scan_status.config(text="Error: No scan object available")
        except ValueError:
            self.scan_status.config(text="Invalid parameters")
    
    def update_scan_ui_state(self):
        """Update the scan UI based on available hardware"""
        scan_ready = (self.backend.camera is not None and
                     self.backend.x_stage is not None and
                     self.backend.y_stage is not None)
        
        if scan_ready:
            self.start_button.config(state="normal")
            self.scan_status.config(text="Ready")
        else:
            self.start_button.config(state="disabled")
            self.scan_status.config(text="Missing hardware - configure in Hardware tab")
    
    def start_scan(self):
        """Start the scan process"""
        if not self.backend.scan:
            messagebox.showerror("Scan Error", "No scan object available")
            return
            
        # Apply current settings
        self.apply_scan_settings()
        
        # Start scan in a separate thread
        self.scan_thread = threading.Thread(target=self._run_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        # Update UI
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.cancel_button.config(state="normal")
        self.resume_button.config(state="disabled")
        self.scan_status.config(text="Scanning...")
    
    def _run_scan(self):
        """Run the scan in a background thread"""
        try:
            self.backend.scan.start_scan()
            
            # Update UI when scan is complete
            if not self.backend.scan.is_running:
                self.root.after(0, self._update_ui_after_scan)
        except Exception as e:
            messagebox.showerror("Scan Error", f"Error during scan: {e}")
            self.root.after(0, self._update_ui_after_scan)
    
    def _update_ui_after_scan(self):
        """Update UI after scan completes"""
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.resume_button.config(state="disabled")
        self.cancel_button.config(state="disabled")
        self.scan_status.config(text="Scan completed")
        self.progress_var.set(100)
    
    def pause_scan(self):
        """Pause the ongoing scan"""
        if self.backend.scan:
            self.backend.scan.pause_scan()
            self.pause_button.config(state="disabled")
            self.resume_button.config(state="normal")
            self.scan_status.config(text="Paused")
    
    def resume_scan(self):
        """Resume a paused scan"""
        if self.backend.scan:
            self.backend.scan.resume_scan()
            self.pause_button.config(state="normal")
            self.resume_button.config(state="disabled")
            self.scan_status.config(text="Scanning...")
    
    def cancel_scan(self):
        """Cancel the current scan"""
        if self.backend.scan:
            self.backend.scan.cancel_scan()
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.resume_button.config(state="disabled")
            self.cancel_button.config(state="disabled")
            self.scan_status.config(text="Canceled")
            self.progress_var.set(0)
    
    def update_progress(self):
        """Update the progress bar based on scan progress"""
        if self.backend.scan and self.backend.scan.is_running:
            current = self.backend.scan.current_image
            total = self.backend.scan.num_x * self.backend.scan.num_y
            if total > 0:  # Avoid division by zero
                progress = (current / total) * 100
                self.progress_var.set(progress)
        
        # Schedule the next update
        self.root.after(100, self.update_progress)
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Stop any running scan
            if self.backend.scan and self.backend.scan.is_running:
                self.backend.scan.cancel_scan()
                
            # Close all hardware connections
            self.backend.close()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            # Destroy the root window
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImagingApp(root)
    root.after(100, app.update_progress)  # Start progress updates
    root.mainloop()