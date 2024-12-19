from pywinauto import Desktop

Desktop(backend='win32').window(title_re ="Open procedure*").wait('exists',5)
