import requests

def verify_license_via_api(license_key):
    """Verify the license key using the remote API."""
    api_url = "http://your-vps-ip:5050/verify_license"  # Replace with your VPS URL or domain
    response = requests.post(api_url, json={"license_key": license_key})

    if response.status_code == 200 and response.json().get("status") == "success":
        print("License verified successfully!")
        return True
    else:
        print("Invalid or expired license key.")
        return False


if __name__ == '__main__':
    user_license = input("Enter your license key: ")

    if verify_license_via_api(user_license):
        print("Access granted. You can now use the Webmail Multi-Sender.")
    else:
        print("Access denied. Please check your license key.")
