@echo off
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$root='C:\Users\Lenovo\Desktop\Codex Agent合集\小红书爆款拆解Agent';" ^
  "$vault='C:\Users\Lenovo\Desktop\小红书\obsidian1';" ^
  "$title=Join-Path $vault '标题库\职场新人成长手册';" ^
  "$cover=Join-Path $vault '封面模版库\职场新人成长手册';" ^
  "[pscustomobject]@{AgentRoot=(Test-Path -LiteralPath $root); LiveAnalysisSkill=(Test-Path -LiteralPath 'C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-hotnote-analysis'); LiveArchiveSkill=(Test-Path -LiteralPath 'C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-report-archive'); PerNoteTitles=(Get-ChildItem -LiteralPath $title -File -Filter '爆款标题*.md').Count; PerNoteCovers=(Get-ChildItem -LiteralPath $cover -File -Filter '爆款封面*.md').Count; PerNoteCoverImages=(Get-ChildItem -LiteralPath (Join-Path $cover '图片') -File -Filter '爆款封面*.jpg').Count} | Format-List"
pause
