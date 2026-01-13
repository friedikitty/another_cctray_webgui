# Deployment Guide for Windows Server with Nginx

This guide explains how to deploy the CCTray Build Status Monitor on a Windows server with nginx.

## Prerequisites

- Windows Server / Linux should work, but not tested
- Python 3.8+ installed
- Nginx installed and running
- Administrator access to add services

## Step 1: Install Dependencies

1. Navigate to the project directory:
```cmd
cd cctray_python
```

2. Create a virtual environment (recommended):
```cmd
python -m venv venv
venv\Scripts\activate
```

3. Install required packages:
```cmd
pip install -r requirements.txt
```

## Step 2: Configure the Application

1. Edit `config.json` to set the port (default: 5001):
```json
{
  "port": 5001,
  "host": "127.0.0.1",
  "threads": 4,
  ...
}
```

**Important:** 
- `host` should be `127.0.0.1` (localhost) so only nginx can access it
- `port` should be a port not used by other services
- `threads` controls concurrent requests (4 is usually good)

## Step 3: Configure Nginx

1. Open your nginx configuration file:
   - Usually located at: `C:\nginx\conf\nginx.conf`
   - Or in your sites configuration

2. Add the following location block inside your `server` block:

```nginx
location /ci_status {
    rewrite ^/ci_status/?(.*) /$1 break;
    proxy_pass http://127.0.0.1:31030;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Script-Name /ci_status;
    
    proxy_http_version 1.1;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

3. Test nginx configuration:
```cmd
nginx -t
```

4. Reload nginx:
```cmd
nginx -s reload
```

## Step 4: Start the Application

### Option A: Manual Start (Development/Testing)

Run the WSGI server:
```cmd
python wsgi.py
```

Or use the batch script:
```cmd
start_server.bat
```

### Option B: Windows Service (Production)

For production, you should run it as a Windows Service. Options:

1. **Using NSSM (Non-Sucking Service Manager)** - Recommended:
   - Download NSSM from https://nssm.cc/download
   - Install the service:
   ```cmd
   nssm install CCTrayMonitor "C:\Python\python.exe" "T:\mh_workspace\messiah_tool\build\cctray_python\wsgi.py"
   nssm set CCTrayMonitor AppDirectory "T:\mh_workspace\messiah_tool\build\cctray_python"
   nssm start CCTrayMonitor
   ```

2. **Using Task Scheduler**:
   - Open Task Scheduler
   - Create Basic Task
   - Trigger: "When the computer starts"
   - Action: Start a program
   - Program: `python.exe`
   - Arguments: `xxx\cctray_python\wsgi.py`
   - Start in: `xxx\cctray_python`

## Step 5: Verify Deployment

1. Open your browser and navigate to:
   ```
   http://your_server_ip/ci_status
   ```

2. You should see the Build Status Monitor dashboard.

3. Check the API endpoint:
   ```
   http://your_server_ip/ci_status/api/status
   ```

## Troubleshooting

### Application won't start
- Check if the port is already in use: `netstat -ano | findstr :5001`
- Verify Python and dependencies are installed: `python --version`
- Check the console output for error messages

### 502 Bad Gateway
- Ensure the Flask app is running on the correct port (check `config.json`)
- Verify nginx can reach `http://127.0.0.1:5001`
- Check Windows Firewall isn't blocking the connection

### 404 Not Found
- Verify the nginx location block is correct
- Check that nginx configuration was reloaded
- Ensure the rewrite rule is correct

### Static files not loading
- Check browser console for 404 errors
- Verify the base path is correctly set in the HTML

## File Structure

```
cctray_python/
├── app.py              # Flask application
├── wsgi.py             # WSGI server (production)
├── config.json         # Configuration
├── requirements.txt    # Python dependencies
├── start_server.bat    # Windows startup script
├── templates/
│   └── index.html      # Web interface
└── DEPLOYMENT.md       # This file
```

## Updating the Application

1. Stop the service (if running as service):
   ```cmd
   nssm stop CCTrayMonitor
   ```

2. Update files as needed

3. Restart the service:
   ```cmd
   nssm start CCTrayMonitor
   ```

Or if running manually, just restart `wsgi.py`.

## Security Notes

- The Flask app runs on `127.0.0.1` (localhost only) - not accessible from outside
- Only nginx should be able to access it
- Consider adding authentication in nginx if needed
- Keep Python and dependencies updated

## Performance Tuning

- Adjust `threads` in `config.json` based on your server capacity
- Monitor memory usage
- Consider using a process manager like Supervisor if needed
