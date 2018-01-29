poc-chatops
=================
Example of Telegram chatbot for remote shell command execution

Configuration and usage
=================
1. Configuration
```
SALT_API_USERNAME = '<salt_api_user>'
SALT_API_PASSWORD = '<salt_api_password>'
SALT_API_EAUTH = 'pam'
SALT_API_URL = '<salt_api_endpoint>'
```

2. Examples of chatbot commands:
- /minions
- /glob "docker01.*" ls 
- /grain "virtual_subtype:Docker" ls
