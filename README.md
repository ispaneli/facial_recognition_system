# Facial recognition system backend (FastAPI and OpenCV)

## 🍎 Errors on Apple silicon (M1, M2, etc.)

### Step 1.
Install official PNG reference library.
```shell
brew install libpng
export C_INCLUDE_PATH=/opt/homebrew/Cellar/libpng/<YOUR_VERSION>/include
export LIBRARY_PATH=/opt/homebrew/Cellar/libpng/<YOUR_VERSION>/lib
```

### Step 2.
Reinstall all packages using **PIP** with flags *--force-reinstall* and *--no-cache-dir*.

For example:
```shell
pip install --upgrade wheel
pip install cmake --force-reinstall --no-cache-dir
pip install dlib --force-reinstall --no-cache-dir
pip install opencv-python --force-reinstall --no-cache-dir
pip install face-recognition --force-reinstall --no-cache-dir
```





