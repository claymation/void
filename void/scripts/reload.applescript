on run argv
    set browser to item 1 of argv
    activate application browser
    tell application "System Events" to keystroke "r" using command down
    activate application "Terminal"
end run
