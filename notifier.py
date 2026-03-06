"""
UpdateAlarm - Windows bildirim yoneticisi
Plyer birincil, PowerShell yedek, tkinter popup son care.
"""
import subprocess
import threading


def _notify_powershell(title: str, message: str):
    title_safe = title.replace('"', "'").replace("\n", " ")
    msg_safe = message.replace('"', "'").replace("\n", " | ")
    script = (
        'Add-Type -AssemblyName System.Windows.Forms;'
        '$n = New-Object System.Windows.Forms.NotifyIcon;'
        '$n.Icon = [System.Drawing.SystemIcons]::Information;'
        f'$n.BalloonTipTitle = "{title_safe}";'
        f'$n.BalloonTipText = "{msg_safe}";'
        '$n.Visible = $true;'
        '$n.ShowBalloonTip(8000);'
        'Start-Sleep -s 9;'
        '$n.Dispose()'
    )
    subprocess.Popen(
        ["powershell", "-WindowStyle", "Hidden", "-Command", script],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _notify_plyer(title: str, message: str):
    from plyer import notification
    notification.notify(
        title=title,
        message=message,
        app_name="Update Alarm",
        timeout=10,
    )


def notify(title: str, message: str):
    """Bildirim gonder - arka planda calisirir, uygulamayi bloklmaz."""
    def _send():
        try:
            _notify_plyer(title, message)
        except Exception:
            try:
                _notify_powershell(title, message)
            except Exception:
                pass  # tkinter popup main.py tarafindan yonetilir

    t = threading.Thread(target=_send, daemon=True)
    t.start()
