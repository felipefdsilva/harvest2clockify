# harvest2clockify
Migrates clients, tasks and projects from Harvest(getharvest.com) to Clockify (clockify.me).

Harvest's exported data must be in csv format. The code expect a folder structure:

```bash
  ├── harvest2clockify.py
  └── harvest_data
      ├── clients.csv
      ├── projects.csv
      └── tasks.csv
```
