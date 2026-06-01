import datetime

def create_employee_folder(employee_name: str, department: str) -> dict:
    """
    Simulates creating a Google Drive folder for a new employee.
    In Week 3, replace this with real Google Drive API calls.
    Returns a simulated folder object with ID and URL.
    """
    # Simulate a Drive folder ID (real Drive IDs look like this)
    safe_name = employee_name.replace(" ", "_")
    folder_id = f"DRIVE_SIM_{safe_name}_{department}_{datetime.date.today().strftime('%Y%m%d')}"
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"  # simulated URL

    return {
        "folder_id": folder_id,
        "folder_name": f"{employee_name} - {department}",
        "folder_url": folder_url,
        "status": "created",
        "created_at": datetime.datetime.now().isoformat()
    }

def create_department_subfolder(employee_name: str, folder_type: str) -> dict:
    """Creates simulated sub-folders like 'Documents', 'Projects'."""
    safe_name = employee_name.replace(" ", "_")
    folder_id = f"DRIVE_SIM_{safe_name}_{folder_type}"
    return {
        "folder_id": folder_id,
        "folder_name": folder_type,
        "status": "created"
    }