Telyzer Structure
```
Telyzer/
│
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── app/
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── channel_controller.py
│   │   └── analysis_controller.py
│   │
│   ├── services/
│   │   ├── telegram_service.py
│   │   ├── session_service.py
│   │   └── database_service.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   │
│   ├── ui/
│   │   ├── windows/
│   │   ├── widgets/
│   │   └── styles/
│   │
│   └── utils/
│
├── data/
│   ├── sessions/  
│   ├── exports/
│   └── .gitkeep
│
├── resources/
│   ├── icons/
│   ├── images/
│   └── fonts/
│
├── config/
│   ├── settings.json
│   └── secrets.json
│
└── docs/
    ├── architecture.md
    ├── setup.md
    └── contribution.md
```