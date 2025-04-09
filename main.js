const { app, BrowserWindow, dialog} = require('electron');
const { spawn } = require('cross-spawn');
const path = require('path');
const fs = require("fs");

const python_cmd = process.platform === "win32" ? "python" : "python3";
const server_path = path.resolve(__dirname, "sources", "Server.py");
const cwd_path = path.resolve(__dirname, "sources");
const venv_dir = path.join(__dirname, "venv");
const requirements_path = path.join(__dirname, "requirements.txt");

let python_available;
let mainWindow;
let flask;

function environment_exists() {
    return fs.existsSync(venv_dir);
}

function create_environment() {
    const venv_create = spawn.sync(python_cmd, ["-m", "venv", venv_dir])
    if (venv_create.error) {
        dialog.showErrorBox("Virtual environment creation", "First time application run tried to create virtual environment for Python backend and failed!\nPlease restart!");
        return false;
    }

    const pip_win = path.join(venv_dir, "Scripts", "pip.exe");
    const pip_unix = path.join(venv_dir, "bin", "pip");
    const pip = process.platform === "win32" ? pip_win : pip_unix;
    const pip_install = spawn.sync(pip, ["install", "-r", requirements_path]);
    if (pip_install.error) {
        fs.rmSync(venv_dir);
        dialog.showErrorBox("Requirements installation", "First time application run tried to install Python dependencies and failed!\nPlease restart!");
        return false;
    }

    return true;
}

function get_python() {
    const folder = process.platform === "win32" ? "Scripts" : "bin";
    const python = path.join(venv_dir, folder, "python");
    python_available = true;
    if (!environment_exists()) {
        dialog.showMessageBox({
            "title": "First time setup",
            "message": "Setting up Python backend!\nApplication will start automatically once this is done."
        });
        python_available = create_environment();
    } 
    return python;
}

app.whenReady().then(() => {
    const python = get_python();
    if (!python_available) {
        return;
    }

    flask = spawn(python, [server_path], {
        cwd: cwd_path,
        stdio: "pipe",
    });

    flask.stdout.on("data", (data) => {
        console.log(`${data}`);
    });
    
    flask.stderr.on("data", (data) => {
        console.error(`${data}`);
    });

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
        },
    });

    mainWindow.loadFile(path.join(__dirname, 'frontend', 'build', 'index.html'));

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
});

app.on('window-all-closed', () => {
    app.quit();
});

app.on('before-quit', () => {
    if (flask) {
        flask.kill();
    }
});