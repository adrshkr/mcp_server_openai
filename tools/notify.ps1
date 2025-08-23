param(
    [string]$Title = "Task Completed",
    [string]$Message = "Claude Code task finished"
)

# Play system sound only - no popup windows
[System.Console]::Beep(800, 200)
Start-Sleep -Milliseconds 100
[System.Console]::Beep(1000, 200)