# Another CCTray WebGUI

- I tried most of the available CCTray viewers on GitHub, but none of them fully fulfill the requirements:
    - CCTray is good, but it displays the web link which may leak passwords
    - Some others are buggy
    - Some others have poor UI design

- The main ideas behind this project are:
    - Prevent password leaks in URLs. TeamCity's CCTray feed requires authentication credentials in the URL, which can be exposed in browser history or logs. This application handles credentials server-side to prevent such leaks.
    - Provide a better-looking UI
    
- Host it on a server so team members don't need to configure anything, preventing configuration errors and password leaks;

- Or you can use it locally as a cctray viewer

- **Simply put:** A Flask-based web application that continuously monitors and displays build status from a CCTray XML feed.

- Looks this:

    - jump to a feed on the top
    - expand/unexpand using the arraw button on the right
    - click `[link]` to jump to the url

    ![image-20260113160433350](README.assets/image-20260113160433350.png)

## Quick Start
* `py -3 -m pip install -r requirements.txt` or `pip install -r requirements.txt`
* Modify `config_user.json5`
  ```json
    "feeds": [
            {
                "name": "name",
                "url": "http://name:password@TeamCityServerURL:8111/httpAuth/app/rest/cctray/projects.xml",
                "filter_regex": "",
                "main_url": "http://TeamCityServerURL:8111"
            },
    ]
  ```
* Run `wsgi.py`
* You can view the feed at the indicated website URL
* Then you may need to review [DEPLOYMENT.md](DEPLOYMENT.md) to deploy it to a server or just use it as a CCTray viewer locally

## Features

- Real-time build status monitoring
- Auto-refreshing dashboard (updates every 5 seconds)
- Beautiful, responsive UI
- Support for multiple build projects
- Configurable via `config.json5` and `config_user.json5`


## Setup

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Tests

Run the unit tests to verify the installation:

```bash
python run_tests.py
```

Or run specific test files:

```bash
python -m unittest test_util.py
```

### Configure the CCTray feed URL in `config_user.json5`:
Read the comments at the top of the file. Feeds are configured like this:
```json
"feeds": [
        {
            "name": "name",
            "url": "http://name:password@TeamCityServerURL:8111/httpAuth/app/rest/cctray/projects.xml",
            "filter_regex": "",
            "main_url": "http://TeamCityServerURL:8111"
        },
        // ... more feeds
]
```

### Run the application:
```bash
# Development mode (with auto-reload enabled by default)
python app.py

# Or explicitly enable debug mode
python app.py --debug

# Production mode (disable auto-reload)
python app.py --no-debug
```

### Open your browser and navigate to:
```
http://localhost:31030
```

## TeamCity Setup Advice
* TeamCity automatically provides the CCTray XML feed
* Don't use a guest account, as that may cause data leakage
* Add a group like `cc_viewer_group` and assign it the "Tool integration" role
* Add a user like `cc_viewer` with password `cc_viewer`, then assign it to the `cc_viewer_group`
* You can then use `http://cc_viewer:cc_viewer@<teamcity-server>/httpAuth/app/rest/cctray/projects.xml` as the feed URL to see the build status
* This URL can be used in your `config_user.json5` configuration

## Development Workflow

**Good news!** You don't need to restart the server for most changes:

- ✅ **HTML templates** (`templates/*.html`) - Auto-reloads automatically (no restart needed)
- ✅ **config.json5** and **config_user.json5** - Loaded on each request, changes take effect immediately (just refresh browser)
- ⚠️ **Python code** (`app.py`) - Requires debug mode for auto-reload:
  - Run with `python app.py` (debug mode enabled by default)
  - The server will automatically restart when you save changes to `app.py`
  - You'll see a message like "Restarting with stat" in the terminal

**Tip:** For the best development experience, always run with debug mode enabled. The server will watch for file changes and reload automatically!

## Configuration

The application uses two configuration files:

### `config_user.json5` - Feed Configuration
Configure your CCTray feeds here. Each feed includes:
- `name`: Display name for the feed
- `url`: The CCTray XML feed URL (supports HTTP basic auth in URL format: `http://user:password@server/path`)
- `filter_regex`: Optional regex pattern to filter projects (leave empty for all projects)
- `main_url`: Base URL for the TeamCity server (used for links)

### `config.json5` - Application Configuration
- Edit `config.json5` to customize the application:

* Just read the comments on the head of the file

## Project Structure

```
.
├── app.py                  # Flask application
├── wsgi.py                 # WSGI entry point for production
├── config.json5            # Application configuration (UI, server settings)
├── config_user.json5       # User configuration (CCTray feeds)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Web interface
├── static/
│   └── images/             # Static assets
└── README.md               # This file
```

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/status` - JSON API returning current build status

## Notes

- The application automatically refreshes the build status every 5 seconds
- Build status colors:
  - Green: Success
  - Red: Failure
  - Orange: Exception
  - Blue: Building/Checking
  - Gray: Unknown



## Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.