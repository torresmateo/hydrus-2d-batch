@echo off
for /d %%d in ( * ) do (
    echo Running Hydrus on %cd%\%%d
    echo %cd%\%%d > LEVEL_01.dir
    %1 < %2
)