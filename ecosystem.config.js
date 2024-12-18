module.exports = {
  apps: [
    {
      name: "python-server",
      script: "python3.11 server.py",
      interpreter: "/var/nepse/NepseAPI/venv/bin/python",
      cwd: "/var/nepse/NepseAPI",
      max_memory_restart: "150M",
    },
    {
      name: "python-socket-server",
      script: "python3.11 socketServer.py",
      interpreter: "/var/nepse/NepseAPI/venv/bin/python",
      cwd: "/var/nepse/NepseAPI",
      max_memory_restart: "150M",
    },
    {
      name: "hono-api",
      script: "dist/index.js",
      cwd: "/var/nepse/nepse_api",
      watch: false,
      max_memory_restart: "250M",
      post_update: ["npm install", "npm run build"],
      env_production: {
        NODE_ENV: "production",
      },
    },
  ],
};
