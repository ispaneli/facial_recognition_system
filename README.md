# Facial recognition system backend (FastAPI and OpenCV)

## ▶️ Quick Start

1. Go to project directory and configure environment variables:
```shell
export FRS_MONGODB_URL="<YOUR_MONGODB_URL>"
export FRS_GLOBAL_SALT="<YOUR_GLOBAL_SALT>"
export FRS_JWT_SECRET_KEY="<YOUR_SSL_SECRET_KEY>"
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

2. Create and activate Python environment:
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements-base.txt
```

3. Start application:
```shell
python3 src/facial_recognition_system/main.py
```

## 🍎 Errors on Apple silicon (M1, M2, etc.)

1. Install official PNG reference library.
```shell
brew install libpng
export C_INCLUDE_PATH=/opt/homebrew/Cellar/libpng/<YOUR_VERSION>/include
export LIBRARY_PATH=/opt/homebrew/Cellar/libpng/<YOUR_VERSION>/lib
```

2. Reinstall all packages using **PIP** with flags *--force-reinstall* and *--no-cache-dir*. For example:
```shell
pip install --upgrade wheel
pip install cmake --force-reinstall --no-cache-dir
pip install dlib --force-reinstall --no-cache-dir
pip install opencv-python --force-reinstall --no-cache-dir
pip install face-recognition --force-reinstall --no-cache-dir
```

## 👁️ OpenCV highlighting problem in PyCharm Professional

* PyCharm;
* Settings...;
* Project: <project_name>;
* Python Interpreter;
* Show all... in list of interpreters;
* select your interpreter;
* press "Show Interpreter Paths";
* add OpenCV-path (for example: */Users/admin/PycharmProjects/facial_recognition_system/venv/lib/python3.10/site-packages/cv2*)




